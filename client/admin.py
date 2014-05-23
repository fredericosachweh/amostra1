# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
import logging
import thread
import requests
from django.contrib.admin import site, ModelAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from django.conf import settings
server_key = settings.NBRIDGE_SERVER_KEY
import models
log = logging.getLogger('client')
from nbridge.models import Nbridge
# from device.forms import GenericRelationForm


def reboot_stbs(queryset, nbridge):
    url = 'http://%s/ws/reboot/' % (nbridge.server.host)
    macs = []
    # mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21
    for s in queryset:
        macs.append(s.mac)
    data = {
        'server_key': server_key,
        'mac[]': [macs]
        }
    log.debug('DATA=%s', data)
    try:
        response = requests.post(url, timeout=10, data=data)
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')


def reboot_stb(modeladmin, request, queryset):
    nbs = Nbridge.objects.filter(status=True)
    for s in nbs:
        thread.start_new_thread(reboot_stbs, (queryset, s))

reboot_stb.short_description = ugettext_lazy(
    'Reiniciar %(verbose_name_plural)s selecionados')


class SetTopBoxChannelInline(admin.TabularInline):
    model = models.SetTopBoxChannel


class SetTopBoxAdmin(ModelAdmin):
    search_fields = ('mac', 'serial_number', 'description', )
    list_display = ('serial_number', 'mac', 'description', 'online', )
    actions = [reboot_stb]
    inlines = [SetTopBoxChannelInline, ]

    def get_readonly_fields(self, request, obj = None):
        if obj:
            return ('mac', 'serial_number', ) + self.readonly_fields
        return self.readonly_fields


class SetTopBoxConfigAdmin(ModelAdmin):
    search_fields = ('settopbox__mac', 'settopbox__serial_number', )
    list_display = ('settopbox', 'key', 'value', )
    list_filter = ('settopbox', )


class SetTopBoxChannelAdmin(ModelAdmin):
    search_fields = ('settopbox__mac', 'settopbox__serial_number', )
    list_display = ('settopbox', 'channel', )
    list_filter = ('settopbox', )


class SetTopBoxMessageAdmin(ModelAdmin):
    #form = GenericRelationForm()
    #model =
    pass

site.register(models.SetTopBox, SetTopBoxAdmin)
#site.register(models.SetTopBoxParameter)
site.register(models.SetTopBoxProgramSchedule)
site.register(models.SetTopBoxChannel, SetTopBoxChannelAdmin)
site.register(models.SetTopBoxConfig, SetTopBoxConfigAdmin)
site.register(models.SetTopBoxMessage, SetTopBoxMessageAdmin)
