"""Models for transcribe."""
import logging
import re
from datetime import timedelta
from os import path
from xml.sax.saxutils import escape

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Max, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import format_html, strip_tags
from model_utils import Choices
from model_utils.models import TimeStampedModel

from transcribe import settings
from transcribe.diff_match_patch import diff_match_patch
from transcribe.utils import html_diffs, remove_markup

log = logging.getLogger(__name__)

User = get_user_model()

AUDIO = 'audio'
FINISHED = 'finished'
IN_PROGRESS = 'in progress'
REVIEW = 'review'
SKIPPED = 'skipped'
TEXT = 'text'
TRANSCRIPTION = 'transcription'
VIDEO = 'video'

MEDIA = Choices(AUDIO, TEXT, VIDEO)

STATUS = Choices(IN_PROGRESS, SKIPPED, FINISHED)

TASK = Choices(TRANSCRIPTION, REVIEW)


def get_transcribe_user(user):
    if not isinstance(user, TranscribeUser):
        user = TranscribeUser.objects.get(user=user)
    return user


def task_file_name(instance, filename):
    """Returns the full path of a task file."""
    return '/'.join(['project_content', str(instance.project.id), filename])


def make_task_count_property(task_type, status):
    """
    Closure to generate a new class cached_property that returns the number of
    tasks with a given task_type and status.
    """

    @cached_property
    def task_counter(self):
        return (
            getattr(self, '{}_tasks'.format(task_type))()
            .filter(status=status)
            .count()
        )

    return task_counter


class TranscribeUserManager(models.Manager):
    """Custom manager for TranscribeUser."""

    def get_queryset(self):
        return super().get_queryset().select_related('user')


class TranscribeUser(models.Model):
    user = models.OneToOneField(
        User, related_name='transcribe_user', on_delete=models.CASCADE
    )

    objects = TranscribeUserManager()

    num_finished_transcriptions = make_task_count_property(
        TRANSCRIPTION, FINISHED
    )
    num_skipped_transcriptions = make_task_count_property(
        TRANSCRIPTION, SKIPPED
    )
    num_in_progress_transcriptions = make_task_count_property(
        TRANSCRIPTION, IN_PROGRESS
    )
    num_finished_reviews = make_task_count_property(REVIEW, FINISHED)
    num_skipped_reviews = make_task_count_property(REVIEW, SKIPPED)
    num_in_progress_reviews = make_task_count_property(REVIEW, IN_PROGRESS)

    @cached_property
    def name(self):
        """Returns the user's name."""
        return '{u.first_name} {u.last_name}'.format(u=self.user)

    @cached_property
    def sort_name(self):
        """Returns the user's sortable name."""
        return '{u.last_name}, {u.first_name}'.format(u=self.user)

    @cached_property
    def is_new(self):
        """Returns if the user is new."""
        num_tasks = self.transcription_tasks().filter(status=FINISHED).count()
        return num_tasks < 1

    @cached_property
    def is_admin(self):
        """Returns if the user is part of the Admin group or a superuser."""
        return (
            self.user.groups.filter(name='Admin').exists()
            or self.user.is_superuser
        )

    @cached_property
    def is_reviewer(self):
        """Returns if the user is part of the Reviewer group."""
        return self.user.groups.filter(name='Reviewer').exists()

    @cached_property
    def num_tasks(self):
        return UserTask.objects.filter(user=self).count()

    @cached_property
    def can_see_projects(self):
        """get projects this user can see"""
        can_see_projects = []
        projects = Project.objects.filter(archived=0)
        for project in projects:
            if project not in can_see_projects:
                if (
                    self.is_admin
                    or project.allow_global_transcriptions
                    or self.can_review_project(project)
                    or self.can_transcribe_project(project)
                ):
                    can_see_projects.append(project)
        return can_see_projects

    @cached_property
    def projects_right_to_transcribe(self):
        """get projects this user has rights to transcribe"""
        projects = self.transcription_projects.filter(archived=0).order_by(
            '-priority'
        )
        return projects

    def can_transcribe_project(self, project):
        # can't transcribe archived projects
        if project.archived == 1:
            return False
        # admins can transcribe any project
        if self.is_admin:
            return True
        # anyone can transcribe this project
        if project.allow_global_transcriptions:
            return True
        # is this project is in this user's transcription_projects
        for p in self.projects_right_to_transcribe:
            if project.pk == p:
                return True
        return False

    @cached_property
    def projects_right_to_review(self):
        """get projects this user has the right to review"""
        projects = self.review_projects.filter(archived=0).order_by(
            '-priority'
        )
        return projects

    def can_review_project(self, project):
        # can't review archived projects
        if project.archived == 1:
            return False
        # admins can review everything
        if self.is_admin:
            return True
        # this user is a reviewer and any reviewer can review this project
        if self.is_reviewer and project.reviewers.count() == 0:
            return True
        # is this project is in this user's review_projects
        for p in self.projects_right_to_review:
            if project.pk == p:
                return True
        return False

    def recent_transcription_tasks(self, num=100):
        """Return transcription tasks."""
        return self.transcription_tasks().prefetch_related(
            'task', 'task__project'
        )[:num]

    def transcription_tasks(self):
        """Return transcription tasks."""
        return self._get_tasks(TRANSCRIPTION)

    def review_tasks(self):
        """Return review tasks."""
        return self._get_tasks(REVIEW)

    def _get_tasks(self, task_type):
        return self.tasks.filter(task_type=task_type).prefetch_related(
            'task', 'task__project'
        )

    def _get_report_stats(self, datetime_start, datetime_end):
        counts = UserTask.objects.filter(user=self).aggregate(
            num_finished_transcriptions=Count(
                'id',
                filter=Q(
                    modified__gte=datetime_start,
                    modified__lte=datetime_end,
                    status='finished',
                    task_type='transcription',
                ),
            ),
            num_finished_reviews=Count(
                'id',
                filter=Q(
                    modified__gte=datetime_start,
                    modified__lte=datetime_end,
                    status='finished',
                    task_type='review',
                ),
            ),
            num_skipped_transcriptions=Count(
                'id',
                filter=Q(
                    modified__gte=datetime_start,
                    modified__lte=datetime_end,
                    status='skipped',
                    task_type='transcription',
                ),
            ),
            num_skipped_reviews=Count(
                'id',
                filter=Q(
                    modified__gte=datetime_start,
                    modified__lte=datetime_end,
                    status='skipped',
                    task_type='review',
                ),
            ),
            num_in_progress_transcriptions=Count(
                'id',
                filter=Q(
                    modified__gte=datetime_start,
                    modified__lte=datetime_end,
                    status='in progress',
                    task_type='transcription',
                ),
            ),
            num_in_progress_reviews=Count(
                'id',
                filter=Q(
                    modified__gte=datetime_start,
                    modified__lte=datetime_end,
                    status='in progress',
                    task_type='review',
                ),
            ),
        )
        self.num_finished_transcriptions = counts[
            'num_finished_transcriptions'
        ]
        self.num_finished_reviews = counts['num_finished_reviews']
        self.num_skipped_transcriptions = counts['num_skipped_transcriptions']
        self.num_skipped_reviews = counts['num_skipped_reviews']
        self.num_in_progress_transcriptions = counts[
            'num_in_progress_transcriptions'
        ]
        self.num_in_progress_reviews = counts['num_in_progress_reviews']

    def roles(self):
        pass

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Transcribe user'
        verbose_name_plural = 'Transcribe users'
        ordering = ['user__last_name', 'user__first_name']


class UserPreferences(models.Model):
    user = models.OneToOneField(
        TranscribeUser, related_name='preferences', on_delete=models.CASCADE
    )
    uses_serif_transcription_font = models.BooleanField(default=True)


class ProjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)

    def archived(self):
        return super().get_queryset().filter(archived=True)

    def everything(self):
        return super().get_queryset()


class TaskQuerySet(models.QuerySet):
    def with_transcription_tasks(self):
        return self.filter(usertasks__task_type=TRANSCRIPTION)

    def finished(self):
        return self.with_transcription_tasks().filter(
            models.Q(usertasks__task_type=REVIEW)
            & models.Q(usertasks__status=FINISHED)
        )

    def annotate_num_usertasks(
        self, annotation='num_usertasks', status=None, task_type=None
    ):
        """
        Annotates the task queryset with the specified annotation named that is
        the number of usertasks attached to the Tasks that satisfy the status
        and task_type given.

        Arguments:
            annotation - the attached annotation attribute name [num_usertasks]
            status - the status of the usertasks
            task_type - the task_type of the usertasks
        """
        annotation_params = {
            annotation: models.Sum(
                models.Case(
                    models.When(
                        usertasks__task_type=task_type,
                        usertasks__status=status,
                        then=models.Value(1),
                    ),
                    default=models.Value(0),
                    output_field=models.IntegerField(),
                )
            )
        }
        return self.annotate(**annotation_params)

    def annotate_num_finished_usertasks(self):
        """
        Annotates the number of finished transcriptions and the number of
        finished reviews. Adds num_finished_transcriptions and
        num_finished_reviews as annotations to the queryset.
        """
        return self.annotate_num_usertasks(
            'num_finished_transcriptions', FINISHED, TRANSCRIPTION
        ).annotate_num_usertasks(  # noqa
            'num_finished_reviews', FINISHED, REVIEW
        )

    def annotate_last_transcribed(self):
        """
        Annotates each task with the modified date of its last finished
        transcription user task. If no finished transcription exists,
        the annotated value will be `None`.
        """
        annotation_params = {
            'last_transcribed': models.Max(
                models.Case(
                    models.When(
                        usertasks__task_type=TRANSCRIPTION,
                        usertasks__status=FINISHED,
                        then='usertasks__modified',
                    ),
                    output_field=models.DateField(),
                )
            )
        }
        return self.annotate(**annotation_params)


class Project(TimeStampedModel):
    """A transcription project."""

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    guidelines = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    transcribers_per_task = models.IntegerField(default=2)
    media_type = models.CharField(max_length=6, default=TEXT, choices=MEDIA)
    archived = models.BooleanField(default=False)
    finding_aid_url = models.CharField(blank=True, max_length=2083)
    transcribers = models.ManyToManyField(
        TranscribeUser, blank=True, related_name='transcription_projects'
    )
    reviewers = models.ManyToManyField(
        TranscribeUser, blank=True, related_name='review_projects'
    )
    allow_global_transcriptions = models.BooleanField(default=False)

    objects = ProjectManager()

    @cached_property
    def media_type_display(self):
        mapping = {TEXT: 'page', AUDIO: 'soundbit', VIDEO: 'segment'}
        return mapping[self.media_type]

    @cached_property
    def num_tasks(self):
        return self.tasks.count()

    @cached_property
    def percent_done(self):
        """Returns an integer indicating the percent complete for the project."""
        counts = Task.objects.filter(project_id=self.pk).aggregate(
            total_tasks=Count('id'),
            finished_review_tasks=Count('id', filter=Q(finished_review=1)),
            finished_transcription_tasks=Count(
                'id', filter=Q(finished_transcription=1)
            ),
        )
        total_tasks = counts['total_tasks']
        finished_review_tasks = counts['finished_review_tasks']
        finished_transcription_tasks = counts['finished_transcription_tasks']
        if total_tasks == 0:
            return 0
        finished_tasks = finished_review_tasks + finished_transcription_tasks
        percent_done = int((finished_tasks / (total_tasks * 2)) * 100)
        return percent_done

    def pending_task(self, user, task_type):
        """
        Returns a UserTask from the project that has been claimed by the current
        user and is in progress.
        """
        return UserTask.objects.filter(
            task__project=self,
            status='in progress',
            task_type=task_type,
            user=user,
        ).first()

    def pending_transcription_task(self, user):
        """
        Returns the user's in progress transcription task from the project.
        """
        return self.pending_task(user, 'transcription')

    def available_transcription_task(self, user):
        """
        Returns the next available transcription task for this project
        and a given user.
        """
        user = get_transcribe_user(user)
        if not user.can_transcribe_project(self):
            return False

        # if there is an in_progress task return that one
        in_progress_task = self.tasks.filter(
            usertasks__user=user,
            usertasks__task_type=TRANSCRIPTION,
            usertasks__status=IN_PROGRESS,
        ).first()
        if in_progress_task:
            return in_progress_task

        tpt = self.transcribers_per_task

        task_ids_to_exclude = set()

        # exclude tasks that are finished being transcribed
        task_ids_to_exclude.update(
            self.tasks.defer('transcription')
            .filter(finished_transcription=True)
            .values_list('id', flat=True)
        )

        # exclude tasks that were already worked on by the current user
        task_ids_to_exclude.update(
            self.tasks.defer('transcription')
            .filter(usertasks__user=user, usertasks__task_type=TRANSCRIPTION)
            .values_list('id', flat=True)
        )

        # store this set - it will be less exclusive and act as a
        # second priority to the set that excludes in progress tasks
        task_ids_to_exclude_priority2 = task_ids_to_exclude.copy()

        # exclude tasks that:
        # - have enough user tasks in progress AND
        # - those user tasks are not too old (expired)
        expired_dt = timezone.now() - timedelta(days=settings.TASK_EXPIRE_DAYS)
        task_ids_to_exclude.update(
            self.tasks.defer('transcription')
            .filter(
                models.Q(usertasks__task_type=TRANSCRIPTION)
                & models.Q(usertasks__status=FINISHED)
                | (
                    models.Q(usertasks__status=IN_PROGRESS)
                    & models.Q(usertasks__modified__gt=expired_dt)
                )
            )
            .annotate(num_ut=models.Count('usertasks', distinct=True))
            .filter(num_ut__gte=tpt)
            .values_list('id', flat=True)
        )

        # return the first available task from the project that isn't in the
        # excluded id list.
        task = self.tasks.exclude(id__in=task_ids_to_exclude).first()
        if not task:
            # if there was no task available use the less exclusive set that includes in progress tasks
            task = self.tasks.exclude(
                id__in=task_ids_to_exclude_priority2
            ).first()
        return task

    def pending_review_task(self, user):
        """
        Returns the user's in progress review task from the project.
        """
        return self.pending_task(user, 'review')

    def available_review_task(self, user):
        """
        Returns a single Task from the project that needs to be reviewed.

        The Task should have two finished transcription user tasks and not have
        a finished or recent in progress review user task.
        """
        user = get_transcribe_user(user)

        if not user.can_review_project(self):
            return False

        # if there is an in_progress task return that one
        in_progress_task = self.tasks.filter(
            usertasks__user=user,
            usertasks__task_type=REVIEW,
            usertasks__status=IN_PROGRESS,
        ).first()
        if in_progress_task:
            return in_progress_task

        # tasks that have at least two finished transcription user tasks
        task_ids_ready_for_review = (
            self.tasks.filter(finished_transcription=True)
            .exclude(finished_review=True)
            .values_list('id', flat=True)
        )

        # tasks that the review has already been skipped by the current user
        task_ids_already_skipped = self.tasks.filter(
            usertasks__status='skipped',
            usertasks__task_type='review',
            usertasks__user=user,
        ).values_list('id', flat=True)

        # in progress tasks that are recent
        expired_dt = timezone.now() - timedelta(days=settings.TASK_EXPIRE_DAYS)
        task_ids_being_reviewed_and_recent = self.tasks.filter(
            usertasks__status='in progress',
            usertasks__task_type='review',
            usertasks__modified__gte=expired_dt,
        ).values_list('id', flat=True)

        # filter for tasks that are ready for review, not already skipped,
        # and that haven't recently entered the review process
        task = (
            self.tasks.filter(id__in=task_ids_ready_for_review)
            .exclude(id__in=task_ids_already_skipped)
            .exclude(id__in=task_ids_being_reviewed_and_recent)
            .first()
        )
        return task

    @cached_property
    def status(self):
        status = 'no tasks'
        if self.percent_done == 100:
            status = 'finished'
        elif self.percent_done > 0:
            status = 'in progress'
        elif self.tasks.exists():
            status = 'new'
        return status

    def get_image_urls(self, task):
        # get a few tasks before and after task
        tasks = Task.objects.filter(
            project=self, pk__gte=(task.pk - 5)
        ).order_by('pk')[:10]
        urls = []
        for task in tasks:
            urls.append(task.file.url)
        urls.sort()
        return urls

    def generate_xml(self):
        """Generates and returns an xml representation of the project."""

        tasks = Task.objects.filter(project=self)
        br_replace = re.compile(re.escape('<br>'), re.IGNORECASE)
        transcription = ''
        # construct a complete transcription from the tasks
        for task in tasks.order_by('file'):
            trans = ''
            # get the transcription
            finished_usertask = task.get_finished_transcription()
            # allow the transcription in the task, if it's marked as finished
            if (
                not finished_usertask
                and task.finished_review == 1
                and task.finished_transcription == 1
            ):
                finished_usertask = UserTask()
                finished_usertask.transcription = task.transcription
            if finished_usertask:
                trans = finished_usertask.transcription
            # remove any <br> tags
            trans = br_replace.sub('', trans)
            # add a <milestone> tag with source media
            trans = f'\n<milestone facs="{task.filename}" />\n' + trans
            transcription += trans

        transcription = transcription.replace('\r\n', '\n')
        transcription = transcription.replace('&nbsp;', '&#160;')
        transcription = transcription.replace('<TEIhead>', '<head>')
        transcription = transcription.replace('</TEIhead>', '</head>')
        xml = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>",
            '<tei>',
            '<teiHeader>',
            '<!-- [ TEI Header information ] -->',
            escape(self.title),
            '</teiHeader>',
            '<text>',
            '<front>',
            '<!-- [ front matter ... ] -->',
            '</front>',
            '<body>',
            transcription,
            '</body>',
            '<back>',
            '<!-- [ back matter ... ] -->',
            '</back>',
            '</text>',
            '</tei>',
        ]
        return '\n'.join(xml)

    def generate_txt(self, page_breaks=True):
        """Generates and returns a text representation of the project."""
        tasks = Task.objects.filter(project=self)

        transcription = [
            self.title,
            'Media Type: {0}'.format(self.media_type),
            'Number of Tasks: {0}'.format(self.num_tasks),
            '{0}% complete'.format(self.percent_done),
        ]
        for task in tasks.order_by('file'):
            if page_breaks:
                transcription.append(
                    '\n----- new task ({0})\n'.format(task.filename)
                )

            finished_trans = task.get_finished_transcription()
            # allow the transcription in the task, if it's marked as finished
            if (
                not finished_trans
                and task.finished_review == 1
                and task.finished_transcription == 1
            ):
                finished_trans = UserTask()
                finished_trans.transcription = task.transcription
            # sanitize
            if finished_trans:
                finished_trans = finished_trans.transcription
                finished_trans = strip_tags(finished_trans)
                finished_trans = finished_trans.strip()
                finished_trans = finished_trans.replace('&amp;', '&')
                finished_trans = finished_trans.replace('&lt;', '<')
                finished_trans = finished_trans.replace('&gt;', '>')
                transcription.append(finished_trans)
            else:
                transcription.append('[no transcription]')

        return '\n'.join(transcription).replace('\r\n', '\n')

    def generate_html(self):
        """Generates and returns an HTML representation of the project."""
        import tempfile

        from lxml import etree

        xml = self.generate_xml()
        html = ''
        temp = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
        temp.write(xml)
        temp.close()
        xslt_path = path.join(
            settings.BASE_DIR, 'templates/transcribe/xsl/tei-html.xsl'
        )
        if not path.isfile(xslt_path):
            xslt_path = path.join(
                path.dirname(__file__), 'templates/transcribe/xsl/tei-html.xsl'
            )
        xml = etree.parse(temp.name)
        xslt = etree.parse(xslt_path)
        transform = etree.XSLT(xslt)

        html = transform(xml)
        return str(html)

    def delete(self, *args, **kwargs):
        '''Remove the project media directory on delete.'''
        for task in self.tasks.all():
            task.file.delete(save=False)
        self.archived = True
        self.save()

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

    def stats(self, datetime_start, datetime_end):
        # stats for project totals (all time)
        stats = Task.objects.filter(project_id=self.pk).aggregate(
            total_tasks=Count('id'),
            total_finished_reviews=Count('id', filter=Q(finished_review=1)),
            total_finished_transcriptions=Count(
                'id', filter=Q(finished_transcription=1)
            ),
        )
        percent_done = 0
        transcriptions_percent_done = 0
        reviews_percent_done = 0
        transcriptions_remaining = 0
        reviews_remaining = 0
        total_finished_tasks = 0
        total_tasks = stats['total_tasks']
        total_finished_reviews = stats['total_finished_reviews']
        total_finished_transcriptions = stats['total_finished_transcriptions']
        if total_tasks > 0:
            total_finished_tasks = (
                total_finished_reviews + total_finished_transcriptions
            )
            percent_done = int(
                (total_finished_tasks / (total_tasks * 2)) * 100
            )
            transcriptions_percent_done = int(
                (total_finished_transcriptions / (total_tasks)) * 100
            )
            reviews_percent_done = int(
                (total_finished_reviews / (total_tasks)) * 100
            )
            transcriptions_remaining = (
                total_tasks - total_finished_transcriptions
            )
            reviews_remaining = total_tasks - total_finished_reviews
        # stats for the given date range
        user_tasks_grouped_by_task_id = (
            UserTask.objects.filter(task__project=self.id)
            .filter(task__finished_transcription=1)
            .filter(status='finished')
            .order_by()  # Reset the default ordering defined in UserTask.meta to avoid issues with .values()
            .values('task__id')
            .annotate(max_modified=Max('modified'))
        ).filter(max_modified__range=[datetime_start, datetime_end])
        finished_transcriptions = (
            user_tasks_grouped_by_task_id.filter(task_type='transcription')
        ).count()
        finished_reviews = (
            user_tasks_grouped_by_task_id.filter(task_type='review')
        ).count()

        return {
            'percent_done': percent_done,
            'transcriptions_percent_done': transcriptions_percent_done,
            'reviews_percent_done': reviews_percent_done,
            'transcriptions_remaining': transcriptions_remaining,
            'reviews_remaining': reviews_remaining,
            'total_tasks': total_tasks,
            'total_finished_transcriptions': total_finished_transcriptions,
            'total_finished_reviews': total_finished_reviews,
            'finished_transcriptions': finished_transcriptions,
            'finished_reviews': finished_reviews,
        }

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-priority', 'title']


class UserProjectPreferences(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='userprojects',
        db_index=True,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        TranscribeUser,
        related_name='projects',
        db_index=True,
        on_delete=models.CASCADE,
    )
    transcription_width = models.IntegerField(blank=True, null=True)
    transcription_height = models.IntegerField(blank=True, null=True)
    transcription_stacked = models.BooleanField(blank=True, default=True)


class Tag(models.Model):
    """A markup tag to be used for marking up the transcription text."""

    # TODO: insert tags from legacy system in id order
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    open_tag = models.TextField()
    close_tag = models.TextField()

    def markup(self, text):
        return '{t.open_tag}{text}{t.close_tag}'.format(t=self, text=text)

    def __str__(self):
        return self.name


class Task(TimeStampedModel):
    """A single task from a project. Page, soundbit, etc."""

    file = models.FileField(upload_to=task_file_name)
    transcription = models.TextField(blank=True)
    project = models.ForeignKey(
        Project, related_name='tasks', db_index=True, on_delete=models.CASCADE
    )
    finished_transcription = models.BooleanField(
        default=False, blank=True, db_index=True
    )
    finished_review = models.BooleanField(
        default=False, blank=True, db_index=True
    )

    objects = TaskQuerySet.as_manager()

    @property
    def filename(self):
        return self.file.name.split('/')[-1]

    @cached_property
    def status(self):
        status = 'new'
        user_tasks = UserTask.objects.filter(task_id=self.id)
        while True:
            trans_tasks = user_tasks.filter(task_type=TRANSCRIPTION)
            if trans_tasks.exists():
                status = 'transcribing'
            else:
                break
            finished_tasks = trans_tasks.filter(status=FINISHED)
            if finished_tasks.count() == self.project.transcribers_per_task:
                status = 'finished by transcribers'
            else:
                break
            review_tasks = user_tasks.filter(task_type=REVIEW)
            if review_tasks.exists():
                status = 'reviewing'
            else:
                break
            if review_tasks.filter(status=FINISHED).count():
                status = 'finished by reviewer'
            break
        return status

    def project_link(self):
        project = self.project
        url = reverse('admin:transcribe_project_change', args=(project.pk,))
        title = project.title
        return format_html('<a href="{url}">{title}</a>', url=url, title=title)

    project_link.short_description = 'Project'

    @cached_property
    def num_usertasks(self):
        return self.usertasks.count()

    def claim_transcription(self, user):
        """
        Returns a UserTask for the current Task and given user for transciption.
        """
        # When working with the user instance and UserTasks the id should be
        # used instead of comparing the objects because the user might not be
        # an instance of the TranscribeUser proxy model, and it needs to be.
        # The ids should be the same though.
        users_usertasks_for_task = (
            self.usertasks.filter(user=user)
            .filter(task_type=TRANSCRIPTION)
            .exclude(status=FINISHED)
        )
        # There are no usertasks for the current user for the current task that
        # are transcription tasks and are not finished.
        if users_usertasks_for_task.count() < 1:
            ut = UserTask()
            ut.user = user
            ut.transcription = self.transcription
            ut.task = self
            ut.save()
        else:
            ut = users_usertasks_for_task.first()
        return ut

    def claim_review(self, user):
        """Returns a UserTask for the current Task and given user for review."""
        # See first comment in claim_transcription about working with the user
        # instance in these methods.
        users_usertasks_for_task = (
            self.usertasks.filter(user=user)
            .filter(task_type=REVIEW)
            .exclude(status=FINISHED)
        )
        # There are no usertasks for the current user for the current task that
        # are review tasks that are not finished.
        if users_usertasks_for_task.count() < 1:
            transcriptions = self.usertasks.filter(
                task_type=TRANSCRIPTION, status=FINISHED
            )
            # If there are more transcriptions than a task in this
            # project is supposed to have, don't use the extras.
            num_tasks = self.project.transcribers_per_task
            transcriptions = transcriptions[:num_tasks]
            ut = UserTask()
            ut.user = user
            if len(transcriptions):
                ut.transcription = self.diff_transcriptions(transcriptions)
            ut.task = self
            ut.task_type = REVIEW
            ut.save()
        else:
            ut = users_usertasks_for_task.first()
        return ut

    @staticmethod
    def diff_transcriptions(transcriptions):
        """
        Given 2 transcription like objects (an object with a
        transcription attribute) this method will generate an html diff of the
        transcriptions.
        """
        # remove any markup in transcriptions
        for t in transcriptions:
            t.transcription = remove_markup(t.transcription)

        if len(transcriptions) == 1:
            # only 1 transcription, no need to diff
            return transcriptions[0].transcription

        text1 = transcriptions[0].transcription
        text2 = transcriptions[1].transcription
        # diff
        dmp = diff_match_patch()
        dmp.Diff_Timeout = 0  # don't timeout
        # diff on words instead of characters
        lineText1, lineText2, lineArray = dmp.diff_linesToWords(text1, text2)
        diffs = dmp.diff_main(lineText1, lineText2, False)
        dmp.diff_charsToLines(diffs, lineArray)

        # diffs = dmp.diff_main(text1, text2)
        # make the diffs array more human readable
        # dmp.diff_cleanupSemantic(diffs)
        # format as HMTL with diffs marked as options
        html = html_diffs(diffs)
        return html

    def get_finished_transcription(self):
        usertasks = UserTask.objects.filter(
            task=self, status='finished', task_type='review'
        )
        return usertasks.first()

    def get_transcriptions(self, status=None):
        transcriptions = self.usertasks.filter(task_type=TRANSCRIPTION)
        if status:
            transcriptions = transcriptions.filter(status=status)
        return transcriptions

    def get_reviews(self, status=None):
        reviews = self.usertasks.filter(task_type=REVIEW)
        if status:
            reviews = reviews.filter(status=status)
        return reviews

    def update_finished_transcription(self):
        tpt = self.project.transcribers_per_task
        if self.get_transcriptions(FINISHED).count() >= tpt:
            self.finished_transcription = True
            self.save()

    def update_finished_review(self):
        if self.get_reviews(FINISHED).count() >= 1:
            self.finished_review = True
            self.save()

    def save(self, *args, **kwargs):
        try:
            task = Task.objects.get(id=self.id)
            if task.file != self.file:
                task.file.delete(save=False)
        except Exception:
            pass
        return super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return self.file.name


class UserTask(TimeStampedModel):
    """An instance of a task from a project worked on my a user."""

    task = models.ForeignKey(
        Task, related_name='usertasks', db_index=True, on_delete=models.CASCADE
    )
    task_type = models.CharField(
        max_length=13, choices=TASK, default=TRANSCRIPTION, db_index=True
    )
    transcription = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=11, choices=STATUS, default=IN_PROGRESS, db_index=True
    )
    user = models.ForeignKey(
        TranscribeUser,
        related_name='tasks',
        db_index=True,
        on_delete=models.CASCADE,
    )

    def get_absolute_url(self):
        return reverse('task_workon', kwargs={'pk': self.pk})

    def admin_link(self):
        url = reverse('admin:transcribe_usertask_change', args=(self.pk,))
        return format_html('<a href="{url}">User Task</a>', url=url)

    admin_link.short_description = 'User Task'

    def task_filename(self):
        return self.task.filename()

    task_filename.short_description = 'Task'

    def task_link(self):
        task = self.task
        url = reverse('admin:transcribe_task_change', args=(task.pk,))
        filename = task.filename
        return format_html(
            '<a href="{url}">{name}</a>', url=url, name=filename
        )

    task_link.short_description = 'Task'

    def project_link(self):
        project = self.task.project
        url = reverse('admin:transcribe_project_change', args=(project.pk,))
        title = project.title
        return format_html('<a href="{url}">{title}</a>', url=url, title=title)

    project_link.short_description = 'Project'
    project_link.admin_order_field = 'task__project'

    def user_admin_display_name(self):
        params = {
            'name': self.user.user.get_full_name(),
            'netid': self.user.user.username,
            'url': reverse(
                'admin:transcribe_transcribeuser_change',
                args=(self.user.user.pk,),
            ),
        }
        return format_html('<a href="{url}">{name} ({netid})</a>', **params)

    user_admin_display_name.short_description = 'User'
    user_admin_display_name.admin_order_field = 'user'

    def save(self, *args, **kwargs):
        # remove any < or > characters in TRANSCRIPTION tasks
        # (but not REVIEW tasks - they are allowed to contain tags)
        if self.task_type == TRANSCRIPTION:
            self.transcription = remove_markup(self.transcription)
        rtn = super().save(*args, **kwargs)
        self.task.update_finished_transcription()
        self.task.update_finished_review()
        return rtn

    def __str__(self):
        return 'Task {} by {}'.format(self.task, self.user)

    class Meta:
        ordering = ['-modified', 'user']
