#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django import forms
import canal
#from django.conf import settings


class CanalForm(forms.ModelForm):

    class Meta:
        model = canal.models.Canal
        fields = ('numero','nome','descricao','logo','sigla','ip','porta',)
