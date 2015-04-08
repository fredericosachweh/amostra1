# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
        ('tv', '0001_initial'),
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamplayer',
            name='stb',
            field=models.ForeignKey(blank=True, to='client.SetTopBox', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamrecorder',
            name='channel',
            field=models.ForeignKey(blank=True, to='tv.Channel', null=True),
            preserve_default=True,
        ),
    ]
