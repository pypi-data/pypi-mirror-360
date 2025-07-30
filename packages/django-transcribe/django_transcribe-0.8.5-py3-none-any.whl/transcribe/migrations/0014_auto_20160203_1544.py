# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0013_userpreferences')]

    operations = [
        migrations.AlterField(
            model_name='userpreferences',
            name='user',
            field=models.OneToOneField(
                related_name='preferences',
                to='transcribe.TranscribeUser',
                on_delete=models.CASCADE,
            ),
        )
    ]
