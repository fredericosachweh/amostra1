# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('device', '0002_auto_20150407_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='EncryptDeviceService',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('content_type', models.ForeignKey(verbose_name='Conex\xe3o com device', to='contenttypes.ContentType', null=True)),
                ('nic_sink', models.ForeignKey(related_name='encrypt_device_service__nic_sink', to='device.NIC')),
                ('nic_src', models.ForeignKey(related_name='encrypt_device_service_nic_src', to='device.NIC')),
            ],
            options={
                'verbose_name': 'Entrada CAS IPv4',
                'verbose_name_plural': 'Entradas CAS IPv4',
            },
            bases=('device.deviceserver',),
        ),
        migrations.DeleteModel(
            name='RealTimeEncript',
        ),
    ]
