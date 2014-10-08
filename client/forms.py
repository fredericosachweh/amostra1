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


class SetTopBoxForm(Form):

    mac = MACAddressFormField()
