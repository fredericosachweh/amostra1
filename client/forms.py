#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.forms import Form
from .fields import MACAddressFormField


class SetTopBoxForm(Form):

    mac = MACAddressFormField()
