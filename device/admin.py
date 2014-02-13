#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Modulo administrativo do controle de midias e gravacoes
"""

from __future__ import unicode_literals
from django.contrib import admin
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes import generic
import models
import forms

from django.contrib.sites.models import Site


def test_all_servers(modeladmin, request, queryset):
    for s in queryset:
        s.connect()
        if s.status is True:
            s.auto_create_nic()

test_all_servers.short_description = ugettext_lazy(
    'Testar %(verbose_name_plural)s selecionados')


def recovery_server(modeladmin, request, queryset):
    for s in queryset:
        devices = models.DeviceServer.objects.filter(server=s, status=True)
        for d in devices:
            d.status = False
            d.save()

recovery_server.short_description = ugettext_lazy(
    'Recuperar %(verbose_name_plural)s selecionados')


class NICInline(admin.TabularInline):
    model = models.NIC


class AdminServer(admin.ModelAdmin):
    readonly_fields = ('status', 'modified', 'msg', 'show_versions')
    list_display = ('__unicode__', 'server_type', 'status', 'msg',
        'switch_link',)
    fieldsets = (
      (None, {
        'fields': (('status', 'modified', 'msg', ),
            ('server_type'),
            ('name', ),
            ('host', 'ssh_port', ),
            ('username', ),
            ('rsakey'),
            ('show_versions'),
        )
      }),
    )
    #inlines = [NICInline]
    actions = [test_all_servers, recovery_server]
    list_per_page = 20


class AdminDevice(admin.ModelAdmin):
    list_display = ('__unicode__', 'status', 'link_status', 'server_status',
        'switch_link')
    list_per_page = 20


class AdminStream(admin.ModelAdmin):
    list_display = ('__unicode__', 'status',)
    list_per_page = 20


class AdminSource(admin.ModelAdmin):
    list_display = ('__unicode__', 'in_use', 'destinations',)
    list_per_page = 20


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
    list_display = ('description', 'frequency', 'symbol_rate', 'polarization',
                    'modulation', 'fec', 'server', 'adapter',
                    'antenna', 'tuned', 'switch_link')
    form = forms.DvbTunerForm
    list_per_page = 20


class AdminIsdbTuner(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('server', 'frequency', 'tuned', 'switch_link')
    form = forms.IsdbTunerForm
    list_per_page = 20


class AdminUnicastInput(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('port', 'interface', 'protocol',
                    'tuned', 'server', 'switch_link')
    form = forms.UnicastInputForm
    list_per_page = 20


class AdminMulticastInput(admin.ModelAdmin):
    actions = [start_device, stop_device, scan_device]
    list_display = ('ip', 'port', 'interface', 'server', 'protocol',
        'tuned', 'switch_link')
    form = forms.MulticastInputForm
    list_per_page = 20


class UniqueIPInline(generic.GenericTabularInline):
    model = models.UniqueIP
    list_per_page = 20


class AdminFileInput(admin.ModelAdmin):
    inlines = [UniqueIPInline, ]
    list_display = ('filename', 'description', 'server', 'repeat',
        'switch_link')
    form = forms.FileInputForm
    list_per_page = 20


class AdminMulticastOutput(admin.ModelAdmin):
    list_display = ('ip', 'port', 'protocol',
        'server', 'interface', 'switch_link')
    fieldsets = (
        (_(u'Servidor'), {
            'fields': ('server',)
        }),
        (_(u'Entrada'), {
            'fields': ('nic_sink', 'content_type', 'object_id')
        }),
        (_(u'Saída'), {
            'fields': ('interface', 'ip', 'port', 'protocol')
        }),
    )
    form = forms.MulticastOutputForm
    list_per_page = 20


class AdminDemuxedService(admin.ModelAdmin):
    list_display = ('sid', 'provider', 'service_desc',
                    'server', 'nic_src', 'sink', 'switch_link')
    form = forms.DemuxedServiceForm
    list_per_page = 20


class AdminStreamRecorder(admin.ModelAdmin):
    list_display = ('server', 'description', 'start_time', 'rotate',
                    'keep_time', 'channel', 'storage', 'switch_link')
    form = forms.StreamRecorderForm
    list_per_page = 20


class AdminUniqueIP(admin.ModelAdmin):
    list_display = ('ip', 'port', 'sink_str', 'src_str')
    exclude = ('sequential',)
    fieldsets = (
        (None, {
            'fields': ('ip', 'port')
        }),
        (_(u'Entrada'), {
            'fields': ('content_type', 'object_id')
        }),
    )
    form = forms.UniqueIPForm
    list_per_page = 20


class AdminSoftTranscoder(admin.ModelAdmin):
    list_display = ('description', 'audio_codec', 'switch_link')
    fieldsets = (
        (_(u'Sobre'), {
            'fields': ('description',)
        }),
        (_(u'Conexão com outros devices'), {
            'fields': ('server', 'nic_sink', 'nic_src', 'content_type',
                'object_id')
        }),
        (_(u'Transcodificador de Áudio'), {
            'fields': ('transcode_audio', 'audio_codec')
        }),
        (_(u'Ganho no Áudio'), {
            'classes': ('collapse', ),
            'fields': ('apply_gain', 'gain_value')
        }),
        (_(u'Offset no Áudio'), {
            'classes': ('collapse', ),
            'fields': ('apply_offset', 'offset_value')
        }),

    )
    form = forms.SoftTranscoderForm
    list_per_page = 20


class AdminStorage(admin.ModelAdmin):
    list_display = ('server', 'description', 'n_recorders', 'n_players',
        'hdd_ssd', 'peso', 'folder', 'switch_link')
    form = forms.StorageForm
    list_per_page = 20


class AdminDigitalTunerHardware(admin.ModelAdmin):
    list_display = ('server', 'id_vendor', 'id_product', 'bus', 'driver',
        'uniqueid', 'adapter_nr')
    form = forms.DigitalTunerHardwareForm
    list_per_page = 20


admin.site.register(models.UniqueIP, AdminUniqueIP)
admin.site.register(models.Server, AdminServer)
admin.site.register(models.Antenna)
admin.site.register(models.DvbTuner, AdminDvbTuner)
admin.site.register(models.IsdbTuner, AdminIsdbTuner)
admin.site.register(models.UnicastInput, AdminUnicastInput)
admin.site.register(models.MulticastInput, AdminMulticastInput)
admin.site.register(models.FileInput, AdminFileInput)
admin.site.register(models.MulticastOutput, AdminMulticastOutput)
admin.site.register(models.DemuxedService, AdminDemuxedService)
admin.site.register(models.StreamRecorder, AdminStreamRecorder)
admin.site.register(models.SoftTranscoder, AdminSoftTranscoder)
admin.site.register(models.Storage, AdminStorage)
#admin.site.register(models.DigitalTunerHardware, AdminDigitalTunerHardware)

admin.site.unregister(Site)
