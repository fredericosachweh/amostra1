#!/usr/bin/env python
# -*- encoding:utf8 -*-
from django import forms
from device.models import *
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin
import canal


class CanalForm(forms.ModelForm):
    class Meta:
        model = canal.models.Canal
        fields = ('numero','nome','descricao','logo','sigla','enabled',
                  'source','epg',)

    def clean(self):
        ret = super(CanalForm,self).clean()
        #raise forms.ValidationError("Campo Logo inválido")
        return ret


class SelectInputFormDvblast(forms.ModelForm):
    gravar = forms.BooleanField(label="Gravar fluxo", required=False)
    
    class Meta:
        model = Dvblast
        widgets = {
            # Solucao para forcar a colocacao do "add outro" link
            'server': RelatedFieldWidgetWrapper(forms.Select(), 
                Dvblast.server.field.rel, admin.site, True),}


class SelectInputFormDemuxedService(forms.ModelForm):
    class Meta:
        model = DemuxedService
        exclude = ('server',)


class SelectInputFormStreamRecorder(forms.ModelForm):
    class Meta:
        model = StreamRecorder
        exclude = ('server',)


class SelectInputFormMulticast(forms.ModelForm):
    class Meta:
        model = MulticastOutput
        exclude = ('server',)
        
        
class SelectInputFormDemuxedService(forms.ModelForm):
    class Meta:
        model = DemuxedService
        exclude = ('server',)