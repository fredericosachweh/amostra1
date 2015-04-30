# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SetTopBoxMail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(verbose_name='Promo\xe7\xe3o')),
                ('message', models.TextField(verbose_name='Hoje est\xe1 liberado o pacote Telecine!')),
                ('created', models.BigIntegerField()),
                ('read', models.BooleanField(default=False, verbose_name='Mensagem lida')),
                ('settopbox', models.ForeignKey(to='client.SetTopBox')),
            ],
            options={
                'ordering': ('settopbox', 'created'),
                'verbose_name': 'Correspond\xeancia',
                'verbose_name_plural': 'Correspond\xeancias',
            },
            bases=(models.Model,),
        ),
    ]
