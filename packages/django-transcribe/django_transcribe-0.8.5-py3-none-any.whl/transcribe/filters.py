from django.contrib import admin

from . import models


class UserFilterForUserTask(admin.SimpleListFilter):
    template = 'admin/show_hide_filter.html'
    title = 'user'
    parameter_name = 'user_id'

    def lookups(self, request, model_admin):
        user_id = request.GET.get('user_id')
        if not user_id:
            return []
        user = models.TranscribeUser.objects.get(user__pk=user_id)
        return [(user_id, user.name.strip() or user)]

    def queryset(self, request, queryset):
        user_pk = request.GET.get('user_id')
        if not user_pk:
            return queryset
        return queryset.filter(user=user_pk)


class TaskFilterForUserTask(admin.SimpleListFilter):
    template = 'admin/show_hide_filter.html'
    title = 'task'
    parameter_name = 'task_id'

    def lookups(self, request, model_admin):
        task_id = request.GET.get('task_id')
        if not task_id:
            return []
        task = models.Task.objects.get(pk=task_id)
        return [(task_id, task.file)]

    def queryset(self, request, queryset):
        task_id = request.GET.get('task_id')
        if not task_id:
            return queryset
        # task = models.Task.objects.get(pk=task_id)
        return queryset.filter(task=task_id)
