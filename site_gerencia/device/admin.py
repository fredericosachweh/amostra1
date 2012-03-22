#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from django.contrib import admin
import models
import forms

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
    actions = ['testa_tudo']
    def testa_tudo(self,request,queryset):
        print(request)
    testa_tudo.sort_descritpion = 'Teste todos os servidores'


class AdminDevice(admin.ModelAdmin):
    list_display = ('__unicode__','status','link_status','server_status','switch_link',)


class AdminStream(admin.ModelAdmin):
    list_display = ('__unicode__','status',)


class AdminDVBDestinationInline(admin.TabularInline):#StackedInline
    model = models.DvbblastProgram
    extra = 3


class AdminDVBSource(admin.ModelAdmin):
    inlines = [AdminDVBDestinationInline,]
    list_display = ('__unicode__','status',)


class AdminSource(admin.ModelAdmin):
    list_display = ('__unicode__','in_use','destinations',)


class AdminDvbTuner(admin.ModelAdmin):
    list_display = ('frequency', 'symbol_rate', 'polarization', 'modulation', 'server', 'adapter', 'antenna')
    form = forms.DvbTunerForm


class AdminIsdbTuner(admin.ModelAdmin):
    list_display = ('server', 'frequency')
    form = forms.IsdbTunerForm

class AdminUnicastInput(admin.ModelAdmin):
    list_display = ('port', 'interface', 'protocol','server')
    form = forms.UnicastInputForm

class AdminMulticastInput(admin.ModelAdmin):
    list_display = ('ip', 'port', 'interface', 'server', 'protocol')
    form = forms.MulticastInputForm

#admin.site.register(models.Channel)
admin.site.register(models.Server,AdminServer)
admin.site.register(models.Vlc,AdminDevice)
admin.site.register(models.Dvblast)
admin.site.register(models.MulticatGeneric,AdminDevice)
admin.site.register(models.MulticatSource,AdminDevice)
admin.site.register(models.MulticatRedirect,AdminDevice)
admin.site.register(models.MulticatRecorder)
admin.site.register(models.Source, AdminSource)
admin.site.register(models.Destination)
admin.site.register(models.Antenna)
admin.site.register(models.DvbTuner, AdminDvbTuner)
admin.site.register(models.IsdbTuner)
admin.site.register(models.UnicastInput, AdminUnicastInput)
admin.site.register(models.MulticastInput, AdminMulticastInput)

