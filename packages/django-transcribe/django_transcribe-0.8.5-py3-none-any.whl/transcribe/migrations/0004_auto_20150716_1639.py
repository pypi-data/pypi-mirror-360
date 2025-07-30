# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0003_transcribeuser')]

    operations = [
        migrations.AlterModelOptions(
            name='transcribeuser',
            options={
                'verbose_name': 'Transcribe user',
                'ordering': ['last_name', 'first_name'],
                'verbose_name_plural': 'Transcribe users',
            },
        )
    ]
