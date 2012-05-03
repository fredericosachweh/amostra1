#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django import forms
import canal
from device.models import Dvblast

from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin

#from django.conf import settings


class CanalForm(forms.ModelForm):

    class Meta:
        model = canal.models.Canal
        fields = ('numero','nome','descricao','logo','sigla','enabled','source','epg',)

class SelectInputForm(forms.ModelForm):
    class Meta:
        model = Dvblast
        widgets = {
            # Workaround to force the placement of the 'add another' link
            'server': RelatedFieldWidgetWrapper(forms.Select(), Dvblast.server.field.rel, admin.site, True),
        }


