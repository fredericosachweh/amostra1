# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tv', '0001_initial'),
        ('client', '0002_settopbox_parent'),
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
                ('channel', models.ForeignKey(to='tv.Channel', unique=True)),
                ('plan', models.ForeignKey(to='client.Plan')),
            ],
            options={
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
