# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('device_id', models.CharField(primary_key=True, serialize=False, max_length=200, help_text='SetTopBox de teste', unique=True, verbose_name='Descri\xe7\xe3o do dispositivo')),
                ('device_type', models.CharField(max_length=100, verbose_name='Tipo de dispositivo', choices=[('stb_iptv', 'STB_IPTV')])),
                ('network_id', models.PositiveSmallIntegerField(default='1', verbose_name='Id da rede')),
                ('network_device_id', models.CharField(help_text='00:1A:D0:BE:EF:5F', unique=True, max_length=200, verbose_name='MAC')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeviceEntitlement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device', models.ForeignKey(to='cas.Device')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entitlement',
            fields=[
                ('channel_id', models.PositiveSmallIntegerField(unique=True, serialize=False, verbose_name='ID do Canal', primary_key=True)),
                ('ip_src', models.IPAddressField(unique=True, verbose_name='Endere\xe7o IP - Origem')),
                ('port_src', models.PositiveSmallIntegerField(default=10000, verbose_name='Porta - Origem')),
                ('ip_dest', models.IPAddressField(unique=True, verbose_name='Endere\xe7o IP - Destino')),
                ('port_dest', models.PositiveSmallIntegerField(default=10000, verbose_name='Porta - Destino')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RTESServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default='RTES1', help_text='Inicialmente deve ser RTES1', unique=True, max_length=200, verbose_name='Nome')),
                ('host', models.IPAddressField(unique=True, verbose_name='Host')),
                ('definition_uri', models.URLField(help_text='https://10.1.1.56:8094/services/RTES?wsdl', verbose_name='URL de descri\xe7\xe3o do servi\xe7o (WSDL)')),
                ('service_uri', models.URLField(help_text='https://10.1.1.56:8094/services/RTES', verbose_name='URL do Web Service')),
                ('username', models.CharField(max_length=200, verbose_name='Usu\xe1rio')),
                ('password', models.CharField(max_length=200, verbose_name='Senha')),
            ],
            options={
                'verbose_name': 'Servidor RTES - Verimatrix',
                'verbose_name_plural': 'Servidores RTES - Verimatrix',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deviceentitlement',
            name='entitlement',
            field=models.ForeignKey(to='cas.Entitlement'),
            preserve_default=True,
        ),
    ]
