#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from models import SetupBox, Pessoa, PushServer
from django.contrib import admin

class AdminSetupBox(admin.ModelAdmin):
    """
    Classe para manipular modelo do SetupBox na administração
    """
    list_display = ['mac', 'connected', 'enabled']

class AdminPushServer(admin.ModelAdmin):
    """
    Classe para manipular modelo do PushServer na administração
    """
    list_display = [
        'hostname', 
        'port', 
        'channels', 
        'broadcast_channels', 
        'published_messages',
        'subscribers',
    ]


admin.site.register(SetupBox, AdminSetupBox)
admin.site.register(PushServer, AdminPushServer)
admin.site.register(Pessoa)

