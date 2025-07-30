# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transcribe', '0007_reviewer_group_addition'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='allow_global_transcriptions',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='reviewers',
            field=models.ManyToManyField(
                blank=True,
                related_name='review_projects',
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='transcribers',
            field=models.ManyToManyField(
                blank=True,
                related_name='transcription_projects',
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
            preserve_default=True,
        ),
    ]
