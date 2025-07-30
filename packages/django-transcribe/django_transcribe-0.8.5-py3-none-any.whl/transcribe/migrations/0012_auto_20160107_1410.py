# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0011_project_finding_aid_url')]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='reviewers',
            field=models.ManyToManyField(
                blank=True,
                to=settings.AUTH_USER_MODEL,
                related_name='review_projects',
            ),
        ),
        migrations.AlterField(
            model_name='project',
            name='transcribers',
            field=models.ManyToManyField(
                blank=True,
                to=settings.AUTH_USER_MODEL,
                related_name='transcription_projects',
            ),
        ),
    ]
