# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0012_auto_20160107_1410')]

    operations = [
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                (
                    'id',
                    models.AutoField(
                        serialize=False,
                        auto_created=True,
                        verbose_name='ID',
                        primary_key=True,
                    ),
                ),
                (
                    'uses_serif_transcription_font',
                    models.BooleanField(default=True),
                ),
                (
                    'user',
                    models.ForeignKey(
                        to='transcribe.TranscribeUser',
                        related_name='preferences',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        )
    ]
