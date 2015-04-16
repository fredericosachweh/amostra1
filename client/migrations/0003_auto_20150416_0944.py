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
                ('value', models.DecimalField(default=0.0, verbose_name='Valor', max_digits=10, decimal_places=2)),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('channels', models.ManyToManyField(to='tv.Channel', verbose_name='Canais')),
            ],
            options={
                'verbose_name': 'Plano',
                'verbose_name_plural': 'Planos',
            },
            bases=(models.Model,),
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
