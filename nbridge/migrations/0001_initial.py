# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nbridge',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('middleware_addr', models.CharField(help_text='Ex. 10.1.1.100:8800', max_length=100, null=True, verbose_name='Middleware', blank=True)),
                ('debug', models.BooleanField(default=False, verbose_name='Debug')),
                ('debug_port', models.PositiveSmallIntegerField(verbose_name='Porta')),
                ('log_level', models.PositiveSmallIntegerField(default=0, help_text='N\xedvel de log para debug interno (0, 1, 2 ou 3)', verbose_name='N\xedvel de log')),
                ('env_val', models.CharField(default='production', help_text='Tipo de execu\xe7\xe3o', max_length=20, verbose_name='Ambiente de execu\xe7\xe3o', choices=[('production', 'Ambiente de Produ\xe7\xe3o'), ('development', 'Ambiente de Desenvolvimento')])),
            ],
            options={
                'ordering': ['server__name'],
                'verbose_name': 'Servidor NBridge',
                'verbose_name_plural': 'Servidores NBridge',
            },
            bases=('device.deviceserver',),
        ),
    ]
