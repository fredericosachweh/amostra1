#!/usr/bin/env python
# -*- encoding:utf8 -*-
from django import forms
from django.utils.translation import ugettext as _
from device.models import DemuxedService, StreamRecorder
from device.models import SoftTranscoder

import fields
import tv

from tv.form_utils.forms import BetterModelForm


class GenericRelationFormWizard(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenericRelationFormWizard, self).__init__(*args, **kwargs)


class ChannelForm(forms.ModelForm):
    class Meta:
        model = tv.models.Channel
        fields = ('number', 'name', 'channelid', 'description', 'enabled',
                  'source',)

    image = fields.ImageField2Wizard(_('Logo'),
        help_text='Imagem do canal',
    )
    audio_config = forms.BooleanField(label="Configurar Audio", required=False)
    gravar_config = forms.BooleanField(label="Configurar Gravação",
required=False)


class DemuxedServiceFormWizard(forms.Form):
    model = DemuxedService.objects
    demuxed_input = forms.ModelChoiceField(model, label=_(u'Entrada'))


class InputChooseForm(forms.Form):
    INPUT_TYPES = (('arquivos_de_entrada', 'Arquivos de entrada'),
                    ('entradas_multicast', 'Entradas IP multicast'),
                    ('entradas_unicast', 'Entradas IP unicast'),
                    ('dvbs', 'Sintonizadores DVB-S/S2'),
                    ('isdb', 'Sintonizadores ISDB-Tb'))
    input_types_field = forms.ChoiceField(label=_(u'Tipo de Entrada'),
choices=INPUT_TYPES,)
    input_stream = fields.DinamicChoiceField(label=_(u'Entrada'))


class StreamRecorderForm(GenericRelationFormWizard):
    class Meta:
        model = StreamRecorder
        exclude = ('nic_sink', 'content_type', 'object_id', 'start_time',
                   'channel')


class AudioConfigsForm(BetterModelForm):
    class Meta:
        model = SoftTranscoder
        list_display = ('audio_codec', 'switch_link')
        fieldsets = (
            (_(u'Conexão com outros devices'), {
                'fields': ('server', 'nic_sink', 'nic_src', 'content_type',
                    'object_id')
            }),
            (_(u'Transcodificador de Áudio'), {
                'fields': ('transcode_audio', 'audio_codec', 'audio_bitrate',
                    'sync_on_audio_track')
            }),
            (_(u'Ganho no Áudio'), {
                'classes': ('collapse',),
                'fields': ('apply_gain', 'gain_value')
            }),
            (_(u'Compressor Dinâmico de Áudio'), {
                'classes': ('collapse',),
                'fields': ('apply_compressor', 'compressor_rms_peak',
                'compressor_attack', 'compressor_release',
                'compressor_threshold', 'compressor_ratio',
                'compressor_knee', 'compressor_makeup_gain')
            }),
            (_(u'Normalizador de Volume'), {
                'classes': ('collapse',),
                'fields': ('apply_normvol',
                            'normvol_buf_size', 'normvol_max_level')
            }),
        )
