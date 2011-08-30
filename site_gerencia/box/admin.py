#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from models         import SetupBox, Pessoa, PushServer
from django.contrib import admin

from django.utils.translation import ugettext as _

class AdminSetupBox(admin.ModelAdmin):
    """
    Classe para manipular modelo do SetupBox na administração
    """
    list_display = ['mac', 
                    'connected', 
                    'enabled',
                    'pushserver']
    
    fieldsets = [
        (None,                             {'fields': ['pushserver']}),
        (_('Status'),                      {'fields': ['connected']}),
        (_('Caracteristicas do SetupBox'), {'fields': ['mac', 'enabled']}),
        
    ]
    
    readonly_fields = ['connected']
    
    class Media():
        js = ('admin/js/pushserver/console.js',)

class AdminPushServer(admin.ModelAdmin):
    """
    Classe para manipular modelo do PushServer na administração
    """
    list_display = [
        'address', 
        'port', 
        'online',
        'hostname', 
        'setupboxes',
        'channels', 
        'broadcast_channels', 
        'subscribers',
        'created',
        'updated',
    ]


admin.site.register(SetupBox, AdminSetupBox)
admin.site.register(PushServer, AdminPushServer)
admin.site.register(Pessoa)

