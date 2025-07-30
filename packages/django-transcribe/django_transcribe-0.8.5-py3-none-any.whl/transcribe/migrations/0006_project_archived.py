# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('transcribe', '0005_auto_20150717_0829')]

    operations = [
        migrations.AddField(
            model_name='project',
            name='archived',
            field=models.BooleanField(default=False),
            preserve_default=True,
        )
    ]
