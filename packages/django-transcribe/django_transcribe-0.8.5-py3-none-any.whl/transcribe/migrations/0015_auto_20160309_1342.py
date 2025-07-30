# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0014_auto_20160203_1544')]

    operations = [
        migrations.AddField(
            model_name='task',
            name='finished_review',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='finished_transcription',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
