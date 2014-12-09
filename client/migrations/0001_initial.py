# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import client.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SetTopBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_number', models.CharField(help_text='N\xfamero serial do SetTopBox', unique=True, max_length=255, verbose_name='N\xfamero serial')),
                ('mac', client.fields.MACAddressField(help_text='Endere\xe7o MAC do SetTopBox', unique=True, max_length=17, verbose_name='Endere\xe7o MAC')),
                ('description', models.CharField(max_length=255, null=True, verbose_name='Descri\xe7\xe3o opcional', blank=True)),
                ('online', models.BooleanField(default=False, verbose_name='On-line')),
                ('ip', models.GenericIPAddressField(protocol='IPv4', default=None, blank=True, null=True, verbose_name='Endere\xe7o IP')),
            ],
            options={
                'verbose_name': 'SetTopBox',
                'verbose_name_plural': 'SetTopBoxes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetTopBoxBehaviorFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='Chave de indentifica\xe7\xe3o da flag de comportamento', max_length=250, verbose_name='Chave', db_index=True)),
                ('value', models.CharField(help_text='Valor do comportamento. Ex. 0.5', max_length=250, verbose_name='Valor', db_index=True)),
                ('value_type', models.CharField(max_length=50, verbose_name='Tipo do parametro')),
            ],
            options={
                'verbose_name': 'Flag de comportamento',
                'verbose_name_plural': 'Flags de comportamento',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetTopBoxChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recorder', models.BooleanField(default=False, verbose_name='Pode acessar conte\xfado gravado')),
            ],
            options={
                'ordering': ('settopbox', 'channel__number'),
                'verbose_name': 'STB <=> Canal (canal habilitado)',
                'verbose_name_plural': 'STBs <=> Canais (canais habilitados)',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetTopBoxConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='Chave do parametro. Ex. VOLUME_LEVEL', max_length=250, verbose_name='Chave', db_index=True)),
                ('value', models.CharField(help_text='Valor do parametro. Ex. 0.5', max_length=250, verbose_name='Valor', db_index=True)),
                ('value_type', models.CharField(max_length=50, verbose_name='Tipo do parametro')),
            ],
            options={
                'verbose_name': 'Configura\xe7\xe3o do Cliente',
                'verbose_name_plural': 'Configura\xe7\xf5es do Cliente',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetTopBoxMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='Chave de indentifica\xe7\xe3o da mensagem', max_length=250, verbose_name='Chave', db_index=True)),
                ('value', models.TextField(verbose_name='Conte\xfado')),
                ('api_reference', models.CharField(help_text='API base para consumo de vari\xe1veis', max_length=250, verbose_name='Referencia de API')),
            ],
            options={
                'verbose_name': 'Mensagem do cliente',
                'verbose_name_plural': 'Mensagens do cliente',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetTopBoxParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='Chave do parametro. Ex. MACADDR', max_length=250, verbose_name='Chave', db_index=True)),
                ('value', models.CharField(help_text='Valor do parametro. Ex. 00:00:00:00:00', max_length=250, verbose_name='Valor', db_index=True)),
            ],
            options={
                'verbose_name': 'Parametro do SetTopBox',
                'verbose_name_plural': 'Parametros dos SetTopBox',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetTopBoxProgramSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField(verbose_name='/tv/api/tv/v1/channel/42/')),
                ('message', models.TextField(verbose_name='Agendamento realizado com sucesso!')),
                ('schedule_date', models.BigIntegerField()),
            ],
            options={
                'ordering': ('settopbox', 'channel__number'),
                'verbose_name': 'Agendamento',
                'verbose_name_plural': 'Agendamentos',
            },
            bases=(models.Model,),
        ),
    ]
