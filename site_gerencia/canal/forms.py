#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django import forms
import canal
from device.models import Dvblast

#from django.conf import settings


class CanalForm(forms.ModelForm):

    class Meta:
        model = canal.models.Canal
        fields = ('numero','nome','descricao','logo','sigla','enabled','source','epg',)

class SelectInputForm(forms.ModelForm):
    class Meta:
        model = Dvblast

