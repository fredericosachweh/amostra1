# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveSmallIntegerField(unique=True, verbose_name='Numero')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(verbose_name='Descricao')),
                ('channelid', models.CharField(max_length=255, verbose_name='ID do Canal')),
                ('image', models.ImageField(help_text='Imagem do canal', upload_to='tv/channel/image/tmp', verbose_name='Logo')),
                ('thumb', models.ImageField(help_text='Imagem do canal', upload_to='tv/channel/image/thumb', verbose_name='Miniatura')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=False, verbose_name='Dispon\xedvel')),
                ('buffer_size', models.PositiveIntegerField(default=1000, help_text='For easy STB 300 > and < 5000', verbose_name='STB Buffer (milisegundos)')),
                ('source', models.ForeignKey(to='device.MulticastOutput')),
            ],
            options={
                'ordering': ('number',),
                'verbose_name_plural': 'Canais',
            },
            bases=(models.Model,),
        ),
    ]
