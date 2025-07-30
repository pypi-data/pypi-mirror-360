# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0008_auto_20150925_1522')]

    operations = [
        migrations.AlterModelOptions(
            name='usertask', options={'ordering': ['-modified', 'user']}
        )
    ]
