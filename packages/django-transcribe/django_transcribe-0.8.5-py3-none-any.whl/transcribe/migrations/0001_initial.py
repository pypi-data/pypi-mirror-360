# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import model_utils.fields
import transcribe.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        verbose_name='created',
                        editable=False,
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        verbose_name='modified',
                        editable=False,
                    ),
                ),
                ('title', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField()),
                ('guidelines', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=0, blank=True)),
                ('transcribers_per_task', models.IntegerField(default=2)),
                (
                    'media_type',
                    models.CharField(
                        default='text',
                        max_length=6,
                        choices=[
                            ('audio', 'audio'),
                            ('text', 'text'),
                            ('video', 'video'),
                        ],
                    ),
                ),
            ],
            options={'ordering': ['-priority', 'title']},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('open_tag', models.TextField()),
                ('close_tag', models.TextField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        verbose_name='created',
                        editable=False,
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        verbose_name='modified',
                        editable=False,
                    ),
                ),
                (
                    'file',
                    models.FileField(
                        upload_to=transcribe.models.task_file_name
                    ),
                ),
                ('transcription', models.TextField(blank=True)),
                (
                    'project',
                    models.ForeignKey(
                        related_name='tasks',
                        to='transcribe.Project',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'abstract': False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserTask',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        verbose_name='created',
                        editable=False,
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        verbose_name='modified',
                        editable=False,
                    ),
                ),
                (
                    'task_type',
                    models.CharField(
                        default='transcription',
                        max_length=13,
                        db_index=True,
                        choices=[
                            ('transcription', 'transcription'),
                            ('review', 'review'),
                        ],
                    ),
                ),
                ('transcription', models.TextField(default='', blank=True)),
                (
                    'status',
                    models.CharField(
                        default='in progress',
                        max_length=11,
                        db_index=True,
                        choices=[
                            ('in progress', 'in progress'),
                            ('skipped', 'skipped'),
                            ('finished', 'finished'),
                        ],
                    ),
                ),
                (
                    'task',
                    models.ForeignKey(
                        related_name='usertasks',
                        to='transcribe.Task',
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        related_name='tasks',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'abstract': False},
            bases=(models.Model,),
        ),
    ]
