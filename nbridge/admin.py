# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import models


class AdminNbridge(admin.ModelAdmin):
    list_display = ('server_desc', 'status', 'switch_link')
    fieldsets = (
        (_('Dados Gerais'), {
            'fields': (
                'server', 'description'
            )
        }),
        (_('Parametros de Inicialização'),{
            'fields': (
                'middleware_addr',
            )
        }),
        (_('Tipo de ambiente'),{
            'fields': (
                'env_val',
            )
        }),
        (_('Debug'), {
            'fields': (
                'debug',
                'debug_port',
                'log_level'
            )
        })
    )

    def server_desc(self, obj):
        return '%s (%s)' % (obj.description, obj.server.host)
    server_desc.short_description = _('Descrição')


admin.site.register(models.Nbridge, AdminNbridge)
