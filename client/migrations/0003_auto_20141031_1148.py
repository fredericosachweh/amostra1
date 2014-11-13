# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_messages(apps, schema_editor):
    SetTopBoxMessage = apps.get_model('client', 'SetTopBoxMessage')
    un = SetTopBoxMessage.objects.filter(key='UNAVAILABLE')
    if un.count() == 0:
        SetTopBoxMessage.objects.create(
            key='UNAVAILABLE',
            value='Não foi possível acessar a lista de canais, o sistema pode estar passando por uma dificuldade técnica, para mais detalhes entre em contato com a sua operadora de TV.',
            api_reference = '/tv/api/tv/v2/channel/'
        )
    un = SetTopBoxMessage.objects.filter(key='CHANNEL_DENIED')
    if un.count() == 0:
        SetTopBoxMessage.objects.create(
            key='CHANNEL_DENIED',
            value='O canal {channel.number} ({channel.name}) não está disponível no seu plano.',
            api_reference = '/tv/api/tv/v2/channel/'
        )
    un = SetTopBoxMessage.objects.filter(key='ACCESS_DENIED')
    if un.count() == 0:
        SetTopBoxMessage.objects.create(
            key='ACCESS_DENIED',
            value='Este equipamento está desabilitado.\r\n\r\nConsulte o provedor para mais informações.',
            api_reference = '/tv/api/tv/v2/channel/'
        )

class Migration(migrations.Migration):

    dependencies = [
        ('client', '0002_auto_20141013_1332'),
    ]

    operations = [
        migrations.RunPython(create_messages),
    ]
