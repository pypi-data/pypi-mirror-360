# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from transcribe.management.commands.fix_permissions import Command

"""
Note:
In addition to the Reviewer group, this migration file also adds the
Admin group and fixes the permissions for proxy classes so that
permission can be assigned to admin to create and edit TranscribeUsers.
"""


def add_reviewer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Reviewer')


def remove_reviewer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Reviewer').delete()


def fix_permissions(*args):
    Command().handle(output=False)


def add_admin_group(apps, schema_editor):
    CT = apps.get_model('contenttypes', 'ContentType')
    user_ct, _ = CT.objects.get_or_create(
        app_label='transcribe', model='TranscribeUser'
    )
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    admin, created = Group.objects.get_or_create(name='Admin')

    permissions = [
        'add_project',
        'change_project',
        'delete_project',
        'add_task',
        'change_task',
        'delete_task',
        'add_usertask',
        'change_usertask',
        'delete_usertask',
        'add_tag',
        'change_tag',
        'delete_tag',
    ]

    user_permissions = ['add_transcribeuser', 'change_transcribeuser']

    permissions = [
        Permission.objects.get(codename=code) for code in permissions
    ]

    [
        Permission.objects.get_or_create(content_type=user_ct, codename=code)
        for code in user_permissions
    ]

    user_permissions = [
        Permission.objects.get(content_type=user_ct, codename=code)
        for code in user_permissions
    ]

    admin.permissions.set(permissions + user_permissions)


def remove_admin_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Admin').delete()


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0006_project_archived')]

    operations = [
        migrations.RunPython(add_reviewer_group, remove_reviewer_group),
        migrations.RunPython(fix_permissions, migrations.RunPython.noop),
        migrations.RunPython(add_admin_group, remove_admin_group),
    ]
