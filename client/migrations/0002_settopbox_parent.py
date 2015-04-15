# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='settopbox',
            name='parent',
            field=models.ForeignKey(related_name='parent_set', on_delete=django.db.models.deletion.SET_NULL, verbose_name='SetTopBox Principal', blank=True, to='client.SetTopBox', null=True),
            preserve_default=True,
        ),
    ]
