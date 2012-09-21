#coding:utf8
import re

from django.utils.translation import ugettext_lazy as _
from django.forms             import fields
from django.db                import models
from django.core              import validators

mac_re = re.compile(r'^([0-9a-fA-F]{2}(:?|$)){6}$')

class MACAddressFormField(fields.RegexField):
    default_error_messages = {
        'invalid': _(u'Entre o endereço MAC válido.'),
    }

    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(mac_re, *args, **kwargs)

class MACAddressField(models.CharField):
    empty_strings_allowed = True
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)
        self.validators.append(validators.RegexValidator(
            regex = mac_re, 
            message = _(u'O endereço de MAC é invalido.')
            ))

    def get_internal_type(self):
        return "CharField"
    
    """
    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)
    """
    
    def get_prep_value(self, value):
        "Deixa todas letras maiúsculas."
        value = value.upper()
        return super(MACAddressField, self).get_prep_value(value)
    
