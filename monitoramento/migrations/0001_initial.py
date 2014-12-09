# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Nome')),
                ('host', models.IPAddressField(unique=True, verbose_name='Host', blank=True)),
                ('username', models.CharField(max_length=200, verbose_name='Usu\xe1rio', blank=True)),
                ('password', models.CharField(max_length=200, verbose_name='Senha', blank=True)),
                ('rsakey', models.CharField(help_text='Exemplo: ~/.ssh/id_rsa', max_length=500, verbose_name='Chave RSA', blank=True)),
                ('ssh_port', models.PositiveSmallIntegerField(default=22, null=True, verbose_name='Porta SSH', blank=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\xdaltima modifica\xe7\xe3o')),
                ('status', models.BooleanField(default=False, verbose_name='Status')),
                ('msg', models.TextField(verbose_name='Mensagem de retorno', blank=True)),
                ('offline_mode', models.BooleanField(default=False)),
                ('http_port', models.PositiveSmallIntegerField(default=80, null=True, verbose_name='Porta HTTP', blank=True)),
                ('http_username', models.CharField(max_length=200, verbose_name='Usu\xe1rio HTTP', blank=True)),
                ('http_password', models.CharField(max_length=200, verbose_name='Senha HTTP', blank=True)),
                ('server_type', models.CharField(max_length=100, verbose_name='Tipo de Servidor', choices=[('monitor', 'Servidor Monitoramento')])),
            ],
            options={
                'verbose_name': 'Servidor de monitoramento',
                'verbose_name_plural': 'Servidores de monitoramento',
            },
            bases=(models.Model,),
        ),
    ]
