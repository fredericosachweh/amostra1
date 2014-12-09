# -*- encoding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models.fields.related import ManyToOneRel
from widgets import ContentTypeSelect

from . import models
from dvbinfo import models as dvbinfo_models


class GenericRelationForm(forms.ModelForm):
    class Meta(object):
        pass

    def __init__(self, *args, **kwargs):
        super(GenericRelationForm, self).__init__(*args, **kwargs)
        try:
            model = self.instance.content_type.model_class()
            model_key = model._meta.pk.name
        except Exception:
            model = self._meta.model
            model_key = 'id'
        self.fields['object_id'].widget = ForeignKeyRawIdWidget(
            rel=ManyToOneRel('object_id', model, model_key),
            admin_site=admin.site
        )
        self.fields['content_type'].widget.widget = ContentTypeSelect(
            'lookup_id_object_id',
            self.fields['content_type'].widget.widget.attrs,
            self.fields['content_type'].widget.widget.choices)


class DvbTunerForm(forms.ModelForm):
    class Meta:
        model = models.DvbTuner
        widgets = {
            'adapter': forms.Select(),
        }
        exclude = ('',)


class DvbTunerAutoFillForm(forms.Form):
    sat = forms.ModelChoiceField(
        dvbinfo_models.Satellite.objects,
        label=_(u'Satélite')
    )
    chan = forms.ChoiceField(label=_(u'Canal'))
    fta = forms.BooleanField(label=_(u'Somente canais FTA'), initial=True)
    freq = forms.CharField(label=_(u'Frequência'))
    sr = forms.CharField(label=_(u'Taxa de símbolos'))
    pol = forms.CharField(label=_(u'Polaridade'))
    mod = forms.CharField(label=_(u'Modulação'))
    fec = forms.CharField(label=u'FEC')


class IsdbTunerForm(forms.ModelForm):
    free_adapters = forms.IntegerField(label=_('Adaptadores livres'))

    class Meta:
        model = models.IsdbTuner
        exclude = ('adapter',)


class IsdbTunerAutoFillForm(forms.Form):
    state = forms.ModelChoiceField(
        dvbinfo_models.State.objects,
        label=_(u'Estado')
    )
    city = forms.ChoiceField(label=_(u'Cidade'))
    chan = forms.ChoiceField(label=_(u'Canal'))
    freq = forms.CharField(label=_(u'Frequência'))


class UnicastInputForm(forms.ModelForm):
    class Meta:
        model = models.UnicastInput
        widgets = {
            'interface': forms.Select(),
            'protocol': forms.RadioSelect(),
        }
        exclude = ('',)


class MulticastInputForm(forms.ModelForm):
    class Meta:
        model = models.MulticastInput
        widgets = {
            'interface': forms.Select(),
            'protocol': forms.RadioSelect(),
        }
        exclude = ('',)

    def clean_ip(self):
        from django.core.exceptions import ValidationError
        ip = self.cleaned_data['ip']
        octet = int(ip.split('.')[0])
        if octet < 224 or octet > 239:
            raise ValidationError(
                _(u'Endereços multicast devem ter o primeiro octeto \
entre 224 e 239.'))
        return ip


class DemuxedServiceForm(GenericRelationForm):
    class Meta:
        model = models.DemuxedService
        exclude = ('',)


class FileInputForm(forms.ModelForm):
    class Meta:
        model = models.FileInput
        widgets = {
            'filename': forms.Select(),
        }
        exclude = ('',)


class MulticastOutputForm(GenericRelationForm):
    class Meta:
        model = models.MulticastOutput
        exclude = ('',)


class StreamRecorderForm(GenericRelationForm):
    class Meta:
        model = models.StreamRecorder
        exclude = ('',)


class UniqueIPForm(GenericRelationForm):
    class Meta:
        model = models.UniqueIP
        exclude = ('',)


class SoftTranscoderForm(GenericRelationForm):
    class Meta:
        model = models.SoftTranscoder
        exclude = ('',)


class StorageForm(forms.ModelForm):
    class Meta:
        model = models.Storage
        exclude = ('n_recorders', 'n_players',)


class DigitalTunerHardwareForm(forms.ModelForm):
    class Meta:
        model = models.DigitalTunerHardware
        exclude = ('',)
