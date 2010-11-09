#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.db import models
from django import forms
from django.utils.translation import ugettext as _
import canal

class CanalForm(forms.ModelForm):
    class Meta:
        model = canal.models.Canal
        fields = ('numero','nome','descricao','logo','sigla','ip','porta',)


