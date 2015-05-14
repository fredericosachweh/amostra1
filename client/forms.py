#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.apps import apps
from django.forms import Form, ModelForm
from .fields import MACAddressFormField


class SetTopBoxFormMixin(object):
    def clean_parent(self):
        parent = self.cleaned_data['parent']
        if parent:
            if parent.parent:
                self._errors['parent'] = self.error_class([
                        'SetTopBox não pode ser o principal, ele já é secundário.'
                ])
            if self.instance.parent_set.exists():
                self._errors['parent'] = self.error_class([
                        'SetTopBox não pode ser secundário, ele já é principal.'
                ])
        return parent


class SetTopBoxMixin(object):
    def clean_parent(self):
        parent = self.cleaned_data['parent']
        if parent:
            if parent.parent:
                self._errors['parent'] = self.error_class([
                    u'SetTopBox não pode ser o principal, ele já é secundário.'
                    #'Parente not be principal, it has a parent.'
                ])
            if self.instance.parent_set.exists():
                self._errors['parent'] = self.error_class([
                    'SetTopBox não pode ser secundário, ele já é principal.'
                    #'SetTopBox can not have parent, ele já é principal.'
                ])
        return parent


class SetTopBoxForm(SetTopBoxMixin, Form):

    mac = MACAddressFormField()


class SetTopBoxAdminForm(SetTopBoxFormMixin, ModelForm):
    class Meta:
        model = apps.get_model('client', 'SetTopBox')
        fields = ('__all__')