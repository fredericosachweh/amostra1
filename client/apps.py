# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ClientConfig(AppConfig):
    name = 'client'
    verbose_name = _('Client')

    def ready(self):
        from . import dispatch
        from dbsettings.utils import set_defaults
        from . import models as clientmodels

        set_defaults(
            clientmodels,
            ('SetTopBox', 'auto_create', False),
            ('SetTopBox', 'auto_add_channel', False),
            ('SetTopBox', 'auto_enable_recorder_access', False),
            ('SetTopBox', 'use_mac_as_serial', True),
        )
