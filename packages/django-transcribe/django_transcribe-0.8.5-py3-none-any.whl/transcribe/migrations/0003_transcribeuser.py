# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('transcribe', '0002_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranscribeUser',
            fields=[],
            options={'proxy': True},
            bases=('auth.user',),
        )
    ]
