#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from models import SetupBox, Pessoa, PushServer
from django.contrib import admin

class AdminSetupBox(admin.ModelAdmin):
    """
    Classe para manipular modelo do SetupBox na administração
    """
    list_display = ['mac', 'status_name', 'enabled']


admin.site.register(SetupBox, AdminSetupBox)
admin.site.register(PushServer)
admin.site.register(Pessoa)

