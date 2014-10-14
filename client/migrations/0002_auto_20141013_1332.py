# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
        ('nbridge', '0001_initial'),
        ('tv', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='settopboxprogramschedule',
            name='channel',
            field=models.ForeignKey(to='tv.Channel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='settopboxprogramschedule',
            name='settopbox',
            field=models.ForeignKey(to='client.SetTopBox'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='settopboxparameter',
            name='settopbox',
            field=models.ForeignKey(to='client.SetTopBox'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='settopboxparameter',
            unique_together=set([('key', 'value', 'settopbox')]),
        ),
        migrations.AddField(
            model_name='settopboxconfig',
            name='settopbox',
            field=models.ForeignKey(to='client.SetTopBox'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='settopboxconfig',
            unique_together=set([('key', 'settopbox')]),
        ),
        migrations.AddField(
            model_name='settopboxchannel',
            name='channel',
            field=models.ForeignKey(to='tv.Channel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='settopboxchannel',
            name='settopbox',
            field=models.ForeignKey(to='client.SetTopBox'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='settopboxchannel',
            unique_together=set([('settopbox', 'channel')]),
        ),
        migrations.AddField(
            model_name='settopbox',
            name='nbridge',
            field=models.ForeignKey(db_constraint=False, default=None, blank=True, to='nbridge.Nbridge', null=True),
            preserve_default=True,
        ),
    ]
