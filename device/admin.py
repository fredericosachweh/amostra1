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
            ('username', 'password',),
            ('rsakey'),
            ('show_versions'),
        )
      }),
    )
    #inlines = [NICInline]
    actions = [test_all_servers, recovery_server]


class AdminDevice(admin.ModelAdmin):
    list_display = ('__unicode__', 'status', 'link_status', 'server_status',
        'switch_link')
    list_per_page = 20


class AdminStream(admin.ModelAdmin):
    list_display = ('__unicode__', 'status',)


class AdminSource(admin.ModelAdmin):
    list_display = ('__unicode__', 'in_use', 'destinations',)


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
    inlines = [UniqueIPInline, ]
    list_display = ('filename', 'description', 'server', 'repeat',
        'switch_link')
    form = forms.FileInputForm


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


class AdminDemuxedService(admin.ModelAdmin):
    list_display = ('sid', 'provider', 'service_desc',
                    'server', 'nic_src', 'sink', 'switch_link')
    form = forms.DemuxedServiceForm
    list_per_page = 20


class AdminStreamRecorder(admin.ModelAdmin):
    list_display = ('server', 'description', 'start_time', 'rotate',
                    'keep_time', 'channel', 'storage', 'switch_link')
    form = forms.StreamRecorderForm


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


class AdminSoftTranscoder(admin.ModelAdmin):
    list_display = ('audio_codec', 'switch_link')
    fieldsets = (
        (_(u'Conexão com outros devices'), {
            'fields': ('server', 'nic_sink', 'nic_src', 'content_type',
                'object_id')
        }),
        (_(u'Transcodificador de Áudio'), {
            'fields': ('transcode_audio', 'audio_codec', 'audio_bitrate',
                'sync_on_audio_track')
        }),
        (_(u'Ganho no Áudio'), {
            'classes': ('collapse', ),
            'fields': ('apply_gain', 'gain_value')
        }),
        (_(u'Compressor Dinâmico de Áudio'), {
            'classes': ('collapse',),
            'fields': ('apply_compressor', 'compressor_rms_peak',
            'compressor_attack', 'compressor_release',
            'compressor_threshold', 'compressor_ratio',
            'compressor_knee', 'compressor_makeup_gain')
        }),
        (_(u'Normalizador de Volume'), {
            'classes': ('collapse',),
            'fields': ('apply_normvol',
                        'normvol_buf_size', 'normvol_max_level')
        }),
    )
    form = forms.SoftTranscoderForm


class AdminStorage(admin.ModelAdmin):
    list_display = ('server', 'description', 'n_recorders', 'n_players',
        'hdd_ssd', 'peso', 'folder', 'switch_link')
    form = forms.StorageForm

#    server = models.ForeignKey(Server)
#    id_vendor = models.CharField(max_length=100)
#    id_product = models.CharField(max_length=100)
#    bus = models.CharField(max_length=100)
#    driver = models.CharField(max_length=100)
#    last_update = models.DateTimeField(auto_now=True)
#    uniqueid = models.CharField(max_length=100, unique=True, null=True)
#    adapter_nr = models.PositiveSmallIntegerField()

class AdminDigitalTunerHardware(admin.ModelAdmin):
    list_display = ('server', 'id_vendor', 'id_product', 'bus', 'driver',
        'uniqueid', 'adapter_nr')
    form = forms.DigitalTunerHardwareForm



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
