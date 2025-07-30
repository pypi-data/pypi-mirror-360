"""Admin site customizations."""
import logging

from django.contrib import admin
from django.db.models import Count
from django.shortcuts import resolve_url, reverse
from django.utils.html import format_html

from . import filters, forms, models

log = logging.getLogger(__name__)


@admin.register(models.UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = (
        'user_admin_display_name',
        'task_link',
        'status',
        'task_type',
        'project_link',
        'modified',
    )
    search_fields = (
        'task__file',
        'status',
        'task_type',
        'user__user__username',
        'user__user__first_name',
        'user__user__last_name',
        'task__project__title',
    )
    fields = (
        'task',
        'file_link',
        'task_type',
        'transcription',
        'status',
        'user',
    )
    raw_id_fields = ('task', 'user')
    readonly_fields = ('file_link',)
    list_filter = [
        filters.UserFilterForUserTask,
        filters.TaskFilterForUserTask,
    ]

    def task_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:transcribe_usertask_change', args=[obj.pk]),
            obj.task,
        )

    task_link.short_description = 'Task'

    def file_link(self, obj):
        if obj.task.file:
            return format_html(
                "<a href='{url}'>See file</a>", url=obj.task.file.url
            )
        else:
            return 'No file'


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'file_link',
        'project_link',
        'num_usertasks_link',
    )
    model = models.Task
    fields = (
        'file',
        'transcription',
        'project',
        'project_link',
        'num_usertasks_link',
    )
    readonly_fields = ('project_link', 'num_usertasks_link')
    search_fields = ('file', 'project__title')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(Count('usertasks'))
        return qs

    def num_usertasks_link(self, obj):
        url = resolve_url('admin:transcribe_usertask_changelist')
        url = '{url}?task_id={id}'.format(url=url, id=obj.id)
        return format_html(
            '<a href="{url}">{num} user tasks</a>',
            num=obj.num_usertasks,
            url=url,
        )

    num_usertasks_link.admin_order_field = 'usertasks__count'

    def file_link(self, obj):
        if obj.file:
            return format_html(
                "<a href='{url}'>See file</a>", url=obj.file.url
            )
        else:
            return 'No file'


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'num_tasks_link')
    readonly_fields = ['num_tasks_link']
    form = forms.ProjectForm
    fieldsets = (
        (
            'Project Information',
            {
                'fields': (
                    'title',
                    'description',
                    'media_type',
                    'guidelines',
                    'priority',
                    'upload_media_files',
                    'transcribers_per_task',
                    'num_tasks_link',
                    'finding_aid_url',
                )
            },
        ),
        (
            'Project Permissions',
            {
                'fields': (
                    'allow_global_transcriptions',
                    'transcribers',
                    'reviewers',
                )
            },
        ),
    )

    def get_readonly_fields(self, request, object=None):
        if object is None:
            # if creating a new Project, allow user to set transcibers_per_task
            return self.readonly_fields
        else:
            # if editing an existing Project, don't allow user to set
            # transcribers_per_task
            return self.readonly_fields + ['transcribers_per_task']

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(Count('tasks'))
        return qs

    def num_tasks_link(self, obj):
        url = resolve_url('admin:transcribe_task_changelist')
        url = '{url}?project_id={id}'.format(url=url, id=obj.id)
        return format_html(
            '<a href="{url}">{num} tasks</a>', num=obj.num_tasks, url=url
        )

    num_tasks_link.admin_order_field = 'tasks__count'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TranscribeUser)
class TranscribeUserAdmin(admin.ModelAdmin):
    readonly_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'groups',
        'usertasks_link',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'user',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'groups',
                    'usertasks_link',
                )
            },
        ),
    )

    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'num_finished_transcriptions',
        'num_skipped_transcriptions',
        'num_in_progress_transcriptions',
        'num_finished_reviews',
        'num_skipped_reviews',
        'num_in_progress_reviews',
    ]
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]

    def username(self, obj):
        return obj.user.username

    username.short_description = 'Username'

    def first_name(self, obj):
        return obj.user.first_name

    first_name.short_description = 'First name'

    def last_name(self, obj):
        return obj.user.last_name

    last_name.short_description = 'Last name'

    def email(self, obj):
        return obj.user.email

    email.short_description = 'Email'

    def groups(self, obj):
        return ', '.join([group.name for group in obj.user.groups.all()])

    groups.short_description = 'Groups'

    def usertasks_link(self, obj):
        url = resolve_url('admin:transcribe_usertask_changelist')
        url = '{url}?user_id={id}'.format(url=url, id=obj.id)

        return format_html(
            '<a href="{url}">{num} tasks</a>', num=obj.num_tasks, url=url
        )

    usertasks_link.short_description = 'User tasks'

    def get_queryset(self, request):
        return self.model.objects.filter(user__is_active=True)
