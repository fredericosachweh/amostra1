#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext as _

from models import *
from forms import *

class AdminServer(admin.ModelAdmin):
    readonly_fields = ('status','modified','msg',)
    list_display = ('__unicode__','server_type','status','msg','switch_link',)
    fieldsets = (
      (None, {
        'fields': (('status', 'modified', 'msg',),
            ('server_type'),
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
    model = DvbblastProgram
    extra = 3


class AdminDVBSource(admin.ModelAdmin):
    class Media:
        js = ('jquery/jquery-1.6.2.js','player.js',)
    inlines = [AdminDVBDestinationInline,]
    list_display = ('__unicode__','status',)
    #fieldsets = ()
    #def __init__(self, model, admin_site):
    #    super(AdminDVBSource,self).__init__( model, admin_site)


class AdminSource(admin.ModelAdmin):
    #class Media:
    #    js = ('jquery/jquery-1.6.2.js','player.js',)
    list_display = ('__unicode__','in_use','destinations',)

class AdminTuner(admin.ModelAdmin):
    class Media:
        js = ('js/tuner.js',)
    form = TunerForm
    fieldsets = (
                 (_(u'Auto-preenchimento'), {
                 'fields' : ('sat', ('trans', 'chan'), 'fta')
                 }),
                 (_(u'Sintonizador digital'), {
                 'fields' : ('server',
                             'name',
                             'adapter',
                             'frequency',
                             'symbol_rate',
                             'modulation',
                             'polarization',
                             'bandwidth',
                             'antenna',
                             )
                 }),
                 )

#admin.site.register(models.Channel)
admin.site.register(Server,AdminServer)
admin.site.register(Vlc,AdminDevice)
admin.site.register(Dvblast)
admin.site.register(MulticatGeneric,AdminDevice)
admin.site.register(MulticatSource,AdminDevice)
admin.site.register(MulticatRedirect,AdminDevice)
admin.site.register(MulticatRecorder)
admin.site.register(Source, AdminSource)
admin.site.register(Destination)
admin.site.register(Antenna)
admin.site.register(Tuner, AdminTuner)


