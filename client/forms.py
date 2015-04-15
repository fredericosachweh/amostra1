#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import
import re

from django.forms import fields, Form
from django.utils.translation import ugettext_lazy as _

MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
mac_re = re.compile(MAC_RE)


class MACAddressFormField(fields.RegexField):
    default_error_messages = {
        'invalid': _('Forneça um endereço MAC Válido'),
    }

    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(mac_re, *args, **kwargs)


class SetTopBoxFormMixin(object):
    def clean_parent(self):
        parent = self.cleaned_data['parent']
        if parent:
            if parent.parent:
                self._errors['parent'] = self.error_class([
                        u'SetTopBox não pode ser o principal, ele já é secundário.'
                ])
            if self.instance.parent_set.exists():
                self._errors['parent'] = self.error_class([
                        'SetTopBox não pode ser secundário, ele já é principal.'
                ])
        return parent


class SetTopBoxForm(SetTopBoxFormMixin, Form):

    mac = MACAddressFormField()