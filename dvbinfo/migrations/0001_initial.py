# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DvbsChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('idiom', models.CharField(max_length=200, null=True, verbose_name='Idioma')),
                ('category', models.CharField(max_length=50, null=True, verbose_name='Categoria')),
                ('codec', models.CharField(max_length=50, null=True, verbose_name='Codec')),
                ('crypto', models.CharField(max_length=50, null=True, verbose_name='Criptografia')),
                ('last_info', models.TextField(null=True)),
                ('last_update', models.DateField(null=True)),
                ('logo', models.CharField(max_length=300, null=True, verbose_name='Logotipo')),
                ('definition', models.CharField(max_length=2, null=True, verbose_name='Defini\xe7\xe3o')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Canal de Sat\xe9lite',
                'verbose_name_plural': 'Canais de Sat\xe9lite',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhysicalChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveSmallIntegerField(verbose_name='Canal f\xedsico')),
                ('city', models.ForeignKey(to='dvbinfo.City')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Satellite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('azimuth_degrees', models.FloatField()),
                ('azimuth_direction', models.CharField(max_length=10)),
                ('info', models.TextField(blank=True)),
                ('logo', models.CharField(max_length=300)),
            ],
            options={
                'ordering': ('azimuth_degrees', 'azimuth_direction'),
                'verbose_name': 'Sat\xe9lite',
                'verbose_name_plural': 'Sat\xe9lites',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transponder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, blank=True)),
                ('band', models.CharField(max_length=20, blank=True)),
                ('frequency', models.PositiveIntegerField()),
                ('symbol_rate', models.PositiveIntegerField()),
                ('polarization', models.CharField(max_length=100)),
                ('fec', models.CharField(max_length=10)),
                ('system', models.CharField(max_length=10, null=True)),
                ('modulation', models.CharField(max_length=10, null=True)),
                ('logo', models.CharField(max_length=300)),
                ('satellite', models.ForeignKey(to='dvbinfo.Satellite')),
            ],
            options={
                'ordering': ('name', 'frequency'),
                'verbose_name': 'Transponder',
                'verbose_name_plural': 'Transponders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VirtualChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.FloatField(verbose_name='Canal virtual')),
                ('name', models.CharField(max_length=200, verbose_name='Nome')),
                ('epg', models.BooleanField(default=False, verbose_name='Guia de programa\xe7\xe3o')),
                ('interactivity', models.BooleanField(default=False, verbose_name='Interatividade')),
                ('physical_channel', models.ForeignKey(verbose_name='Canal f\xedsico', to='dvbinfo.PhysicalChannel')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Canal de TV Digital',
                'verbose_name_plural': 'Canais de TV Digitais',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dvbschannel',
            name='transponder',
            field=models.ForeignKey(to='dvbinfo.Transponder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(to='dvbinfo.State'),
            preserve_default=True,
        ),
    ]
