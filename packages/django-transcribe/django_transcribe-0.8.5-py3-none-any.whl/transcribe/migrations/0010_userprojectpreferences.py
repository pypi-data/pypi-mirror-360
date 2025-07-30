# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0009_auto_20150929_1314')]

    operations = [
        migrations.CreateModel(
            name='UserProjectPreferences',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        verbose_name='ID',
                        serialize=False,
                        primary_key=True,
                    ),
                ),
                (
                    'transcription_width',
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    'transcription_height',
                    models.IntegerField(blank=True, null=True),
                ),
                ('transcription_stacked', models.BooleanField(default=True)),
                (
                    'project',
                    models.ForeignKey(
                        related_name='userprojects',
                        to='transcribe.Project',
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        related_name='projects',
                        to='transcribe.TranscribeUser',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        )
    ]
