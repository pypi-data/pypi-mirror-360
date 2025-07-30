# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0004_auto_20150716_1639')]

    operations = [
        migrations.AlterField(
            model_name='usertask',
            name='user',
            field=models.ForeignKey(
                related_name='tasks',
                to='transcribe.TranscribeUser',
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        )
    ]
