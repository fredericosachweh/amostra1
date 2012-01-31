#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from django.contrib import admin

import models

class AdminServer(admin.ModelAdmin):
    readonly_fields = ('status','modified','msg',)
    list_display = ('__unicode__','status','msg','switch_link',)
    fieldsets = (
      (None, {
        'fields': (('status', 'modified', 'msg',),
            ('name',), 
            ('host', 'ssh_port',), 
            ('username', 'password',),
            ('rsakey'),
        )
      }),
    )

class AdminDevice(admin.ModelAdmin):
    class Media:
        js = ('jquery/jquery-1.6.2.js','player.js',)
    list_display = ('__unicode__','status','link_status','server_status','switch_link',)

class AdminStream(admin.ModelAdmin):
    #class Media:
    #    js = ('jquery/jquery-1.6.2.js','player.js',)
    list_display = ('__unicode__','status',)


class AdminDVBDestinationInline(admin.TabularInline):#StackedInline
    model = models.DvbblastProgram
    extra = 3

class AdminDVBSource(admin.ModelAdmin):
    class Media:
        js = ('jquery/jquery-1.6.2.js','player.js',)
    inlines = [AdminDVBDestinationInline,]
    list_display = ('__unicode__','status',)
    #fieldsets = ()
    #def __init__(self, model, admin_site):
    #    super(AdminDVBSource,self).__init__( model, admin_site)
    
    


#admin.site.register(models.Channel)
admin.site.register(models.Server,AdminServer)
admin.site.register(models.Vlc,AdminDevice)
admin.site.register(models.Dvblast)
admin.site.register(models.Multicat,AdminDevice)
admin.site.register(models.MulticatRecorder)



