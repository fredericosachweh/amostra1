# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, choices=[('reload-channels', 'Recarregar lista de canais'), ('reboot-stbs', 'Reiniciar SetTopBoxes'), ('accept-recorder', 'Liberar canais para acessar grava\xe7\xe3o'), ('refuse-recorder', 'Bloquear canais para acessar grava\xe7\xe3o'), ('reload-frontend-stbs', 'Reiniciar frontend dos SetTopBoxes')])),
                ('pks_list', models.TextField()),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('end_at', models.DateTimeField(auto_now=True)),
                ('is_finished', models.BooleanField(default=False)),
                ('progress', models.DecimalField(default=0.0, max_digits=5, decimal_places=2)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
