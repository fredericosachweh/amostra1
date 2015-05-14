# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tv', '0001_initial'),
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Nome')),
                ('slug', models.SlugField()),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('order', models.IntegerField(null=True, blank=True)),
                ('value', models.DecimalField(default=0.0, verbose_name='Valor', max_digits=10, decimal_places=2)),
                ('tvod_value', models.DecimalField(default=0.0, verbose_name='TVoD Valor', max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Plano',
                'verbose_name_plural': 'Planos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlanChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel', models.ForeignKey(verbose_name='Canal', to='tv.Channel', unique=True)),
                ('plan', models.ForeignKey(to='client.Plan')),
            ],
            options={
                'verbose_name': 'Canal do plano',
                'verbose_name_plural': 'Canais do plano',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='plan',
            name='channels',
            field=models.ManyToManyField(to='tv.Channel', verbose_name='Canais', through='client.PlanChannel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='settopbox',
            name='parent',
            field=models.ForeignKey(related_name='parent_set', on_delete=django.db.models.deletion.SET_NULL, verbose_name='SetTopBox Principal', blank=True, to='client.SetTopBox', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='settopbox',
            name='plan',
            field=models.ForeignKey(verbose_name='Plano', blank=True, to='client.Plan', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='settopbox',
            name='plan_date',
            field=models.DateField(null=True, verbose_name='Data de ades\xe3o do plano', blank=True),
            preserve_default=True,
        ),
    ]
