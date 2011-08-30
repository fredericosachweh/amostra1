#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from models         import SetupBox, Pessoa, PushServer
from django.contrib import admin
from django.forms   import ModelForm

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

class SetupBoxInlineForm(ModelForm): 
    def __init__(self, *args, **kwargs): 
        super(SetupBoxInlineForm, self).__init__(*args, **kwargs) 
        self.fields['inside_room'].queryset = SetupBox.objects.filter() 

class SetupBoxInline(admin.TabularInline):
    model = SetupBox 
    extra = 0

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
    
    fieldsets = [
        (_(u'Informações do servidor'), {'fields': ( 
            ('online', 'hostname', 'created'), 
            ('channels', 'broadcast_channels', 'subscribers', 'published_messages',), 
            )}),
        (_(u'Caracteristicas do PushServer'), {'fields': ['schema', 'address', 'port']}),
        
    ]
    
    readonly_fields = ['hostname', 
                       'channels', 
                       'broadcast_channels', 
                       'subscribers', 
                       'published_messages', 
                       'online',
                       'created']
    
    inlines = [SetupBoxInline]


admin.site.register(SetupBox, AdminSetupBox)
admin.site.register(PushServer, AdminPushServer)
admin.site.register(Pessoa)

