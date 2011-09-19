#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from django.contrib import admin

import models

class AdminStream(admin.ModelAdmin):
    #class Media:
    #    js = ('jquery/jquery-1.6.2.js','player.js',)
    list_display = ('__unicode__','status',)



class AdminDVBDestinationInline(admin.TabularInline):#StackedInline
    model = models.DVBDestination
    extra = 1

class AdminDVBSource(admin.ModelAdmin):
    class Media:
        js = ('jquery/jquery-1.6.2.js','player.js',)
    inlines = [AdminDVBDestinationInline,]
    fieldsets = ()
    #def __init__(self, model, admin_site):
    #    super(AdminDVBSource,self).__init__( model, admin_site)
    


#admin.site.register(models.Channel)
admin.site.register(models.MediaMulticastDestination)
admin.site.register(models.MediaMulticastSource)
admin.site.register(models.MediaRecord)
admin.site.register(models.Record)
admin.site.register(models.Stream,AdminStream)
admin.site.register(models.DVBSource,AdminDVBSource)



