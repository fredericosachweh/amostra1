# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_auto_20150423_1050'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='planchannel',
            options={'verbose_name': 'Canal do plano', 'verbose_name_plural': 'Canais do plano'},
        ),
        migrations.AddField(
            model_name='plan',
            name='tvod_value',
            field=models.DecimalField(default=0.0, verbose_name='TVoD Valor', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='plan',
            name='value',
            field=models.DecimalField(default=0.0, verbose_name='Valor', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='planchannel',
            name='channel',
            field=models.ForeignKey(verbose_name='Canal', to='tv.Channel', unique=True),
            preserve_default=True,
        ),
    ]
