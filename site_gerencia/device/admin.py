#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from django.contrib import admin
from django.contrib.contenttypes import generic
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
    list_display = ('__unicode__','status','link_status','server_status',
        'switch_link')


class AdminStream(admin.ModelAdmin):
    list_display = ('__unicode__','status',)


class AdminSource(admin.ModelAdmin):
    list_display = ('__unicode__','in_use','destinations',)


class AdminDvbTuner(admin.ModelAdmin):
    list_display = ('frequency', 'symbol_rate', 'polarization',
                    'modulation', 'fec', 'server', 'adapter',
                    'antenna', 'switch_link')
    form = forms.DvbTunerForm


class AdminIsdbTuner(admin.ModelAdmin):
    list_display = ('server', 'frequency', 'switch_link')
    form = forms.IsdbTunerForm


class AdminUnicastInput(admin.ModelAdmin):
    list_display = ('port', 'interface', 'protocol','server', 'switch_link')
    form = forms.UnicastInputForm


class AdminMulticastInput(admin.ModelAdmin):
    list_display = ('ip', 'port', 'interface', 'server', 'protocol',
        'switch_link')
    form = forms.MulticastInputForm


class UniqueIPInline(generic.GenericTabularInline):
    model = models.UniqueIP


class AdminFileInput(admin.ModelAdmin):
    inlines = [UniqueIPInline,]
    list_display = ('filename', 'server', 'repeat', 'switch_link')
    form = forms.FileInputForm


class AdminMulticastOutput(admin.ModelAdmin):
    list_display = ('ip_out', 'port', 'protocol',
        'server', 'interface', 'switch_link')
    form = forms.MulticastOutputForm


admin.site.register(models.UniqueIP)
admin.site.register(models.Server,AdminServer)
admin.site.register(models.Antenna)
admin.site.register(models.DvbTuner, AdminDvbTuner)
admin.site.register(models.IsdbTuner, AdminIsdbTuner)
admin.site.register(models.UnicastInput, AdminUnicastInput)
admin.site.register(models.MulticastInput, AdminMulticastInput)
admin.site.register(models.FileInput, AdminFileInput)
admin.site.register(models.MulticastOutput, AdminMulticastOutput)
admin.site.register(models.DemuxedService)
admin.site.register(models.StreamRecorder)
