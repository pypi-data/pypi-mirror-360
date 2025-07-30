# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0015_auto_20160309_1342')]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='priority',
            field=models.IntegerField(default=0),
        )
    ]
