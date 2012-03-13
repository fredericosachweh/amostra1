# -*- encoding:utf-8 -*-

from django import forms
from models import *
from dvbinfo.models import *
from django.utils.translation import ugettext as _

class TunerForm(forms.ModelForm):
    # TODO: use reverse() to get the URLs for the javascript
    sat = forms.ModelChoiceField(Satellite.objects, 
                                 label=_(u'Satélite'), 
                                 widget=forms.Select(attrs={'onchange' : 'populate_selects(this.value);'}))
    trans = forms.ModelChoiceField(Transponder.objects.filter(channel__crypto__iexact='FTA'), 
                                   label=_(u'Transponder'), 
                                   widget=forms.Select(attrs={'onchange' : 'transponder_fill_form(this.value);'}))
    chan = forms.ModelChoiceField(Channel.objects.filter(crypto__iexact='FTA'), 
                                  label=_(u'Canal'), 
                                  widget=forms.Select(attrs={'onchange' : 'channel_fill_form(this.value);'}))
    fta = forms.BooleanField(label=_(u'Somente canais FTA'), 
                             initial=True, 
                             widget=forms.CheckboxInput(attrs={'onchange' : 'populate_selects(django.jQuery("select#id_sat").attr("value"));'}))
    
    class Meta:
        model = Tuner