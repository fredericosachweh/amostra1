#!/usr/bin/env python
# -*- encoding:utf8 -*-
from __future__ import unicode_literals
from django import forms
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from . import fields
import tv

from tv.form_utils.forms import BetterModelForm


class GenericRelationFormWizard(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenericRelationFormWizard, self).__init__(*args, **kwargs)


class ChannelForm(forms.ModelForm):
    class Meta:
        model = tv.models.Channel
        fields = (
            'number', 'name', 'channelid', 'description', 'enabled', 'source'
        )
    Channel = apps.get_model('epg', 'Channel')
    epg_model = Channel.objects.all()
    epg_values = []
    for m in epg_model:
        epg_values.append((m.channelid, m.channelid))
    channelid = forms.ChoiceField(label=_('ID do EPG'), choices=epg_values)
    image = fields.ImageField2Wizard(_('Logo'), help_text='Imagem do canal')
    audio_config = forms.BooleanField(label="Configurar Audio", required=False)
    gravar_config = forms.BooleanField(
        label="Configurar Gravação", required=False
    )


class InputChooseForm(forms.Form):
    INPUT_TYPES = (
        ('arquivos_de_entrada', 'Arquivos de entrada'),
        ('entradas_multicast', 'Entradas IP multicast'),
        ('entradas_unicast', 'Entradas IP unicast'),
        ('dvbs', 'Sintonizadores DVB-S/S2'),
        ('isdb', 'Sintonizadores ISDB-Tb')
    )
    input_types_field = forms.ChoiceField(
        label=_('Tipo de Entrada'), choices=INPUT_TYPES
    )
    input_stream = fields.DinamicChoiceField(label=_('Entrada'))
    demuxed_input = fields.DinamicChoiceFieldDemux(label=_('Demux'))


class StreamRecorderForm(GenericRelationFormWizard):
    class Meta:
        model = apps.get_model('device', 'StreamRecorder')
        exclude = (
            'nic_sink', 'content_type', 'object_id', 'start_time', 'channel'
        )


class AudioConfigsForm(BetterModelForm):
    class Meta:
        model = apps.get_model('device', 'SoftTranscoder')
        list_display = ('audio_codec', 'switch_link')
        fieldsets = (
            (_('Conexão com outros devices'), {
                'fields': (
                    'server', 'nic_sink', 'nic_src', 'content_type', 'object_id'
                )
            }),
            (_('Transcodificador de Áudio'), {
                'fields': ('transcode_audio', 'audio_codec')
            }),
            (_('Ganho no Áudio'), {
                'classes': ('collapse',),
                'fields': ('apply_gain', 'gain_value')
            }),
            (_('Offset no Áudio'), {
                'classes': ('collapse',),
                'fields': ('apply_offset', 'offset_value')
            }),
        )
