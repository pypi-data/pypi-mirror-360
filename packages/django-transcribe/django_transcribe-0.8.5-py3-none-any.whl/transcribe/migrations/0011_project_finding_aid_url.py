# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0010_userprojectpreferences')]

    operations = [
        migrations.AddField(
            model_name='project',
            name='finding_aid_url',
            field=models.CharField(blank=True, max_length=2083),
            preserve_default=True,
        )
    ]
