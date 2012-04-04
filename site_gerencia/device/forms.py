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
    fec = forms.CharField(label=u'FEC')

class IsdbTunerForm(forms.ModelForm):
    class Meta:
        model = IsdbTuner
    
    def clean_free_adapters(self):
        fa = int(self.cleaned_data['free_adapters'])
        if fa <= 0:
            from django.core.exceptions import ValidationError
            raise ValidationError(_(u'Deve haver pelo menos 1 adaptador disponível para uso.'))
        return self.cleaned_data['free_adapters']
    
    free_adapters = forms.IntegerField(label=_('Adaptadores livres'))

class IsdbTunerAutoFillForm(forms.Form):
    state = forms.ModelChoiceField(State.objects, label=_(u'Estado'))
    city = forms.ChoiceField(label=_(u'Cidade'))
    chan = forms.ChoiceField(label=_(u'Canal'))
    freq = forms.CharField(label=_(u'Frequência'))

class UnicastInputForm(forms.ModelForm):
    class Meta:
        model = UnicastInput
        widgets = {
            'interface' : forms.Select(),
            'protocol' : forms.RadioSelect(),
        }

class MulticastInputForm(forms.ModelForm):
    class Meta:
        model = MulticastInput
        widgets = {
            'interface' : forms.Select(),
            'protocol' : forms.RadioSelect(),
        }
    
    def clean_ip(self):
        from django.core.exceptions import ValidationError
        ip = self.cleaned_data['ip']
        octet = int(ip.split('.')[0])
        if octet < 224 or octet > 239:
            raise ValidationError(_(u'Endereços multicast devem ter o primeiro octeto entre 224 e 239.'))
        return ip
