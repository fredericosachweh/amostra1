# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import

import re


from django.db import models
from .forms import MACAddressFormField

MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
mac_re = re.compile(MAC_RE)

class MACAddressField(models.CharField):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^client\.fields\.MACAddressField"])