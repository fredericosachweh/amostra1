# -*- encoding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from django.contrib import admin
from django.core.urlresolvers import reverse
from models import *
from dvbinfo.models import *

class DvbTunerForm(forms.ModelForm):
    class Meta:
        model = DvbTuner
        widgets = {
            'adapter' : forms.Select(),
        }

class DvbTunerAutoFillForm(forms.Form):
    sat = forms.ModelChoiceField(Satellite.objects, label=_(u'Satélite'))
    chan = forms.ChoiceField(label=_(u'Canal'))
    fta = forms.BooleanField(label=_(u'Somente canais FTA'), initial=True)
    freq = forms.CharField(label=_(u'Frequência'))
    sr = forms.CharField(label=_(u'Taxa de símbolos'))
    pol = forms.CharField(label=_(u'Polaridade'))
    mod = forms.CharField(label=_(u'Modulação'))

class IsdbTunerForm(forms.ModelForm):
    class Meta:
        model = IsdbTuner
    
    free_adapters = forms.IntegerField(label=_('Adaptadores livres'))
