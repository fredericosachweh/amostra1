# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
        ('client', '0002_auto_20141013_1332'),
        ('contenttypes', '0001_initial'),
        ('tv', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamrecorder',
            name='channel',
            field=models.ForeignKey(blank=True, to='tv.Channel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamrecorder',
            name='content_type',
            field=models.ForeignKey(verbose_name='Conex\xe3o com device', to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamrecorder',
            name='nic_sink',
            field=models.ForeignKey(verbose_name='Interface de rede interna', to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamrecorder',
            name='storage',
            field=models.ForeignKey(to='device.Storage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamplayer',
            name='content_type',
            field=models.ForeignKey(verbose_name='Conex\xe3o com device', to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamplayer',
            name='recorder',
            field=models.ForeignKey(to='device.StreamRecorder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='streamplayer',
            name='stb',
            field=models.ForeignKey(blank=True, to='client.SetTopBox', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='softtranscoder',
            name='content_type',
            field=models.ForeignKey(verbose_name='Conex\xe3o com device', to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='softtranscoder',
            name='nic_sink',
            field=models.ForeignKey(related_name='soft_transcoder_nic_sink', to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='softtranscoder',
            name='nic_src',
            field=models.ForeignKey(related_name='soft_transcoder_nic_src', to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nic',
            name='server',
            field=models.ForeignKey(to='device.Server'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='nic',
            unique_together=set([('name', 'server')]),
        ),
        migrations.AddField(
            model_name='multicastoutput',
            name='content_type',
            field=models.ForeignKey(verbose_name='Conex\xe3o com device', to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multicastoutput',
            name='interface',
            field=models.ForeignKey(verbose_name='Interface de rede externa', to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multicastoutput',
            name='nic_sink',
            field=models.ForeignKey(related_name='nic_sink', verbose_name='Interface de rede interna', to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multicastinput',
            name='interface',
            field=models.ForeignKey(verbose_name='Interface de rede', to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fileinput',
            name='nic_src',
            field=models.ForeignKey(to='device.NIC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dvbtuner',
            name='antenna',
            field=models.ForeignKey(verbose_name='Antena', to='device.Antenna'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='digitaltunerhardware',
            name='server',
            field=models.ForeignKey(to='device.Server'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='digitaltunerhardware',
            unique_together=set([('server', 'adapter_nr')]),
        ),
        migrations.AddField(
            model_name='deviceserver',
            name='server',
            field=models.ForeignKey(verbose_name='Servidor de recursos', to='device.Server'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='demuxedservice',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='demuxedservice',
            name='nic_src',
            field=models.ForeignKey(blank=True, to='device.NIC', null=True),
            preserve_default=True,
        ),
    ]
