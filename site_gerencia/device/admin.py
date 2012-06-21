#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
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


def start_device(modeladmin, request, queryset):
    [device.start() for device in queryset.all()]
start_device.short_description = ugettext_lazy(
    "Iniciar %(verbose_name_plural)s selecionados")

def stop_device(modeladmin, request, queryset):
    [device.stop() for device in queryset.all()]
stop_device.short_description = ugettext_lazy(
    "Parar %(verbose_name_plural)s selecionados")

def scan_device(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    url = '%s?ct=%d&ids=%s' % (reverse('device.views.inputmodel_scan'),
        ct.pk, ",".join(selected))
    return HttpResponseRedirect(url)
scan_device.short_description = ugettext_lazy(
    "Escanear %(verbose_name_plural)s selecionados")

class AdminDvbTuner(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('frequency', 'symbol_rate', 'polarization',
                    'modulation', 'fec', 'server', 'adapter',
                    'antenna', 'tuned', 'switch_link')
    form = forms.DvbTunerForm


class AdminIsdbTuner(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('server', 'frequency', 'tuned', 'switch_link')
    form = forms.IsdbTunerForm


class AdminUnicastInput(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('port', 'interface', 'protocol',
                    'tuned', 'server', 'switch_link')
    form = forms.UnicastInputForm


class AdminMulticastInput(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('ip', 'port', 'interface', 'server', 'protocol',
        'tuned', 'switch_link')
    form = forms.MulticastInputForm


class UniqueIPInline(generic.GenericTabularInline):
    model = models.UniqueIP


class AdminFileInput(admin.ModelAdmin):
    inlines = [UniqueIPInline,]
    list_display = ('filename', 'server', 'repeat', 'switch_link')
    form = forms.FileInputForm


class AdminMulticastOutput(admin.ModelAdmin):
    list_display = ('ip', 'port', 'protocol',
        'server', 'interface', 'switch_link')
    fieldsets = (
        (_(u'Servidor'), {
            'fields' : ('server',)
        }),
        (_(u'Entrada'), {
            'fields' : ('nic_sink', 'content_type', 'object_id')
        }),
        (_(u'Saída'), {
            'fields' : ('interface', 'ip', 'port', 'protocol')
        }),
    )
    form = forms.MulticastOutputForm


class AdminDemuxedService(admin.ModelAdmin):
    list_display = ('sid', 'provider', 'service_desc',
                    'server', 'sink', 'switch_link')
    form = forms.DemuxedServiceForm


class AdminStreamRecorder(admin.ModelAdmin):
    list_display = ('server', 'start_time', 'rotate',
                    'keep_time', 'channel', 'switch_link')
    form = forms.StreamRecorderForm


class AdminUniqueIP(admin.ModelAdmin):
    list_display = ('ip', 'port', 'sink_str', 'src_str')
    exclude = ('sequential',)
    fieldsets = (
        (None, {
            'fields' : ('ip', 'port')
        }),
        (_(u'Entrada'), {
            'fields' : ('content_type', 'object_id')
        }),
    )
    form = forms.UniqueIPForm

admin.site.register(models.UniqueIP, AdminUniqueIP)
admin.site.register(models.Server,AdminServer)
admin.site.register(models.Antenna)
admin.site.register(models.DvbTuner, AdminDvbTuner)
admin.site.register(models.IsdbTuner, AdminIsdbTuner)
admin.site.register(models.UnicastInput, AdminUnicastInput)
admin.site.register(models.MulticastInput, AdminMulticastInput)
admin.site.register(models.FileInput, AdminFileInput)
admin.site.register(models.MulticastOutput, AdminMulticastOutput)
admin.site.register(models.DemuxedService, AdminDemuxedService)
admin.site.register(models.StreamRecorder, AdminStreamRecorder)
admin.site.register(models.SoftTranscoder)
