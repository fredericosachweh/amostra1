#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from models         import SetupBox, SetupBoxCommands, Pessoa, PushServer
from django.contrib import admin
from django.forms   import ModelForm

from django.utils.translation import ugettext as _

class SetupBoxCommandsInlineForm(ModelForm): 
    def __init__(self, *args, **kwargs): 
        super(SetupBoxCommandsInlineForm, self).__init__(*args, **kwargs) 
        self.fields['inside_room'].queryset = SetupBoxCommands.objects.filter() 

class SetupBoxCommandsInline(admin.TabularInline):
    model = SetupBoxCommands 
    can_delete = False
    extra = 1
    max_num = model.objects.count() + 1
    # XXX command tem que ser readonly, usar formset pra exibir campo pro response
    readonly_fields = ['response', 'sended', 'ping', 'created',]

class AdminSetupBox(admin.ModelAdmin):
    """
    Classe para manipular modelo do SetupBox na administração
    """
    list_display = ['mac', 
                    'connected', 
                    'enabled',
                    'pushserver',
                    'updated',
                    'created',
                    ]
    fieldsets = [
        (None, {
            'fields': ['pushserver']
            }),
        (_('Status'), {
           'fields': (('connected', 'created', 'updated', ), ), 
           }),
        (_('Caracteristicas do SetupBox'), {
            'fields': (('mac', 'enabled', ), ), 
            }),
    ]
    readonly_fields = ['connected', 
                       'created', 
                       'updated',
                       ]
    inlines = [SetupBoxCommandsInline]
    
class SetupBoxInlineForm(ModelForm): 
    def __init__(self, *args, **kwargs): 
        super(SetupBoxInlineForm, self).__init__(*args, **kwargs) 
        self.fields['inside_room'].queryset = SetupBox.objects.filter() 

class SetupBoxInline(admin.TabularInline):
    model = SetupBox
    can_order = True 
    extra = 0
    readonly_fields = ['mac']

class AdminPushServer(admin.ModelAdmin):
    """
    Classe para manipular modelo do PushServer na administração
    """
    list_display = ['address', 
                    'port', 
                    'online',
                    'hostname', 
                    'setupboxes',
                    'channels', 
                    'broadcast_channels', 
                    'subscribers',
                    'updated',
                    'created',
                    ]
    fieldsets = [
        (_(u'Informações do servidor'), 
         {'fields': ( 
            ('online', 'hostname', 'created', ), 
            ('channels', 'broadcast_channels', 'subscribers', 'published_messages', ), 
            )
          }),
        (_(u'Caracteristicas do PushServer'), 
         {'fields':( 
            ('schema', 'address', 'port', ),
            ('broadcast_channel', ),
            )
          }),
        ]
    readonly_fields = ['hostname', 
                       'channels', 
                       'broadcast_channels', 
                       'subscribers', 
                       'published_messages', 
                       'online',
                       'created',
                       ]
    inlines = [SetupBoxInline]


admin.site.register(SetupBox, AdminSetupBox)
admin.site.register(PushServer, AdminPushServer)
admin.site.register(Pessoa)

