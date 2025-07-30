import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from transcribe import models, settings
from transcribe.views import mixins

log = logging.getLogger(__name__)


def get_project_with_tasks(project, user):
    """Return project with transcription and review tasks attached."""
    if not isinstance(user, models.TranscribeUser):
        user = models.TranscribeUser.objects.get(user=user)
    project.pending_trans_task = project.pending_transcription_task(user)
    project.avail_trans_task = False
    if not project.pending_trans_task:
        project.avail_trans_task = project.available_transcription_task(user)

    project.pending_review_task_ = project.pending_review_task(user)
    project.avail_review_task = False
    if not project.pending_review_task_:
        project.avail_review_task = project.available_review_task(user)
    tasks = [
        project.avail_trans_task,
        project.avail_review_task,
        project.pending_trans_task,
        project.pending_review_task_,
    ]
    project.available_tasks = any(tasks)
    return project


def landing_page(request):
    """Landing page providing a login link and information.

    Redirects to dashboard if user is authenticated.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'transcribe/web/landing_page.html')


@login_required
def help(request):
    """General help page for the whole site."""
    return render(
        request,
        'transcribe/web/help.html',
        {'support_email': settings.SUPPORT_EMAIL},
    )


@login_required
def faq(request):
    """General FAQ page for the whole site."""
    return render(
        request,
        'transcribe/web/faq.html',
        {'support_email': settings.SUPPORT_EMAIL},
    )


def ping_view(request):
    echo = request.GET.get('echo', '')

    payload = {'working': True}

    if echo:
        payload['echo'] = echo

    return JsonResponse(payload)


def display404(request, exception):
    return render(request, 'transcribe/errors/404.html')


def display500(request):
    return render(request, 'transcribe/errors/500.html')


class DashboardView(
    mixins.ActiveUsersOnlyMixin, mixins.TranscribeUserContextMixin, View
):
    def get(  # noqa C901, TODO simplify this method
        self, request, *args, **kwargs
    ):
        all_tasks = kwargs.get('all_tasks', False)
        context = super().get_context_data()
        context['projects'] = []
        user = context['transcribe_user']

        # how many tasks to retrieve
        # note: all pending tasks will be retrieved
        # even if there are more than max_tasks
        max_tasks = 1000 if all_tasks else 5
        context['all_tasks'] = all_tasks

        # 'in progress' tasks for this user
        user_tasks_in_progress = (
            models.UserTask.objects.defer('transcription')
            .filter(status='in progress', user=user)
            .select_related('task__project')
            .all()
        )
        for t in user_tasks_in_progress:
            project = t.task.project
            # ignore tasks from archived projects
            if project.archived:  
                continue
            # Ignore tasks that are already finished
            if 'finished' in t.task.status:
                continue
            # add project
            if t.task_type == 'review':
                project.pending_review_task_ = t
                context['projects'].append(project)
            if t.task_type == 'transcription':
                project.pending_trans_task = t
                context['projects'].append(project)

        # projects with available review tasks
        if len(context['projects']) < max_tasks:
            projects_available_review = (
                models.Project.objects.defer('tasks__transcription')
                .filter(
                    archived=0,
                    tasks__finished_transcription=1,
                    tasks__finished_review=0,
                )
                .distinct()
                .order_by('-priority')
            )
            for project in projects_available_review:
                if not user.can_review_project(project):
                    continue
                # check for a pending review task in this project
                pending_task = False
                for p in context['projects']:
                    if p.id == project.id and hasattr(
                        p, 'pending_review_task_'
                    ):
                        pending_task = True
                if pending_task:
                    continue
                # add the task
                # if project.available_review_task(user): # enabling this if clause is more accurate but slower
                project.avail_review_task = True
                context['projects'].append(project)
                # we only need max_tasks
                if len(context['projects']) >= max_tasks:
                    break

        # projects with available transcription tasks
        if len(context['projects']) < max_tasks:
            projects_available_transcription = (
                models.Project.objects.defer('tasks__transcription')
                .filter(archived=0, tasks__finished_transcription=0)
                .distinct()
                .order_by('-priority')
            )
            for project in projects_available_transcription:
                if not user.can_transcribe_project(project):
                    continue
                # check for a pending transcription task in this project
                pending_task = False
                for p in context['projects']:
                    if p.id == project.id and hasattr(p, 'pending_trans_task'):
                        pending_task = True
                if pending_task:
                    continue
                # add the task
                # if project.available_transcription_task(user): # enabling this if clause is more accurate but slower
                project.avail_trans_task = True
                context['projects'].append(project)
                # we only need max_tasks
                if len(context['projects']) >= max_tasks:
                    break

        # context['projects'] = list(projects.values())
        context['available_tasks'] = any(context['projects'])
        return render(request, 'transcribe/web/dashboard.html', context)


class ProjectClaimTaskView(mixins.ActiveUsersOnlyMixin, View):
    def get(self, request, pk=None, type=None):
        """
        Creates a UserTask for a given project and user, then redirects to the
        UserTask page or the dashboard if something failed.
        """
        if type not in {'transcription', 'review', 'any'}:
            raise Http404

        failed = False
        user_task = None
        user = models.TranscribeUser.objects.get(user=request.user)

        try:
            project = models.Project.objects.get(pk=pk)
        except models.Project.DoesNotExist:
            failed = True
        else:
            if type == 'transcription':
                task = project.available_transcription_task(user)
                if task:
                    user_task = task.claim_transcription(user)
                else:
                    failed = True
            elif type == 'review' and user.can_review_project(project):
                task = project.available_review_task(user)
                if task:
                    user_task = task.claim_review(user)
                else:
                    failed = True
            elif type == 'any':
                # look for tasks in this order:
                # - any pending task
                # - a review task
                # - a transcription task
                task = project.pending_review_task(user)
                user_task = task
                if not task:
                    task = project.pending_transcription_task(user)
                    if task:
                        user_task = task
                if not task:
                    task = project.available_review_task(user)
                    if task:
                        user_task = task.claim_review(user)
                if not task:
                    task = project.available_transcription_task(user)
                    if task:
                        user_task = task.claim_transcription(user)
                # no task available for this user
                if not task:
                    failed = True

        if not failed and user_task:
            return redirect('task_workon', pk=user_task.pk)
        else:
            messages.error(
                request,
                'Could not claim task. (Another user is probably working on it.)',
            )
            return redirect('dashboard')


class ProjectDownloadView(mixins.AdminUsersOnlyMixin, View):
    def get(self, request, pk, type):
        """Downloads the specified file type export for the project."""
        try:
            project = models.Project.objects.get(pk=pk)
        except models.Project.DoesNotExist:
            messages.add_message(
                request, messages.ERROR, 'Project does not exist.'
            )
            return redirect('dashboard')

        if type == 'xml':
            result = project.generate_xml()
            content_type = 'application/xml'
        elif type == 'txt':
            result = project.generate_txt()
            content_type = 'text/plain'
        elif type == 'html':
            result = project.generate_html()
            content_type = 'text/html'
        else:
            messages.add_message(
                request, messages.ERROR, 'Invalid export type.'
            )
            return redirect('dashboard')
        return HttpResponse(result, content_type=content_type)


class ProjectListView(
    mixins.ActiveUsersOnlyMixin, mixins.TranscribeUserContextMixin, ListView
):
    """List view for projects."""

    model = models.Project
    template_name = 'transcribe/web/projects_list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = []
        # only show projects this user can see
        user = context['transcribe_user']
        can_see_projects = user.can_see_projects
        project_ids = []
        for p in can_see_projects:
            project_ids.append(p.pk)
        if len(project_ids) == 0:
            # there are no projects this user can see
            return context

        # get the projects along with some stats about them
        projects = (
            models.Project.objects.filter(pk__in=project_ids)
            .annotate(
                num_tasks=Count('tasks__id'),
                finished_review_tasks=Count(
                    'tasks__id', filter=Q(tasks__finished_review=True)
                ),
                finished_transcription_tasks=Count(
                    'tasks__id', filter=Q(tasks__finished_transcription=True)
                ),
            )
            .order_by('-priority')
        )

        context['projects'] = projects
        return context


class ProjectDetailView(
    mixins.ActiveUsersOnlyMixin, mixins.TranscribeUserContextMixin, DetailView
):
    """Detail view for a single project."""

    model = models.Project
    template_name = 'transcribe/web/project.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        project = get_project_with_tasks(self.object, self.request.user)
        context['project'] = project
        return context


class UserTaskUpdateView(
    mixins.ActiveUsersOnlyMixin, mixins.AjaxableResponseMixin, UpdateView
):
    """Update view for a UserTask."""

    model = models.UserTask
    template_name = 'transcribe/web/task_edit.html'
    fields = ('task', 'task_type', 'transcription', 'status')

    def _get_user_project_preferences(self):
        user = self.object.user
        project = self.object.task.project
        preferences_list = user.projects.filter(project=project)
        if preferences_list:
            result = preferences_list[0]
        else:
            preferences = models.UserProjectPreferences()
            preferences.user = user
            preferences.project = project
            preferences.save()
            result = preferences
        if len(preferences_list) > 1:
            msg = (
                '{num} UserProjectPreferencess associated with User {user} '
                'and Project {project}. Should only have one '
                'UserProjectPreferences for each User-Project pair.'
            ).format(num=len(preferences_list), user=user, project=project)
            log.error(msg)
        return result

    def _get_user_preferences(self):
        user = self.object.user
        try:
            return user.preferences
        except models.UserPreferences.DoesNotExist:
            result = models.UserPreferences(user=user)
            result.save()
            return result

    def get_context_data(self, **kwargs):
        context = super(UserTaskUpdateView, self).get_context_data(**kwargs)
        context['tags'] = models.Tag.objects.all()
        context['project_preferences'] = self._get_user_project_preferences()
        context['user_preferences'] = self._get_user_preferences()
        project = self.object.task.project
        context['pages'] = project.get_image_urls(self.object.task)
        return context

    def _add_message(self, target_msg, adder):
        msg_storage = messages.get_messages(self.request)
        for msg in msg_storage:
            if msg == target_msg:
                break
        else:
            adder(self.request, target_msg)
        msg_storage.used = False

    def _add_success_message(self):
        success_msg = 'Your transcription was saved'
        self._add_message(success_msg, messages.success)

    def _add_error_message(self):
        success_msg = 'Could not save your transcription'
        self._add_message(success_msg, messages.error)

    def form_valid(self, form):
        response = super(UserTaskUpdateView, self).form_valid(form)
        if response.status_code in (200, 302) and not self.request.is_ajax():
            self._add_success_message()
            return redirect('dashboard')
        elif response.status_code not in (200, 302):
            self._add_error_message()
        return response


class UserPreferencesUpdateView(mixins.ActiveUsersOnlyMixin, UpdateView):
    model = models.UserPreferences
    fields = ['uses_serif_transcription_font']
    success_url = '/'


class UserProjectPreferencesUpdateView(
    mixins.ActiveUsersOnlyMixin, UpdateView
):
    model = models.UserProjectPreferences
    fields = [
        'transcription_width',
        'transcription_height',
        'transcription_stacked',
    ]
    success_url = '/'
