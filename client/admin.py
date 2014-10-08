# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
import thread
import requests
from django.contrib.admin import site, ModelAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from django.conf import settings
server_key = settings.NBRIDGE_SERVER_KEY
from . import models
from nbridge.models import Nbridge

log = logging.getLogger('client')


def reload_channels_stb(modeladmin, request, queryset):
    message='Lista de canais atualizada'
    for s in queryset:
        s.reload_channels(message=message, channel=False)


reload_channels_stb.short_description = ugettext_lazy(
    'Recarregar canais para %(verbose_name_plural)s selecionados')


def start_remote_debug(modeladmin, request, queryset):
    for s in queryset:
        s.remote_debug()

start_remote_debug.short_description = ugettext_lazy(
    'DEBUG %(verbose_name_plural)s selecionados')


def reboot_stbs(queryset, nbridge):
    url = 'http://%s/ws/reboot/' % (nbridge.server.host)
    log.debug('URL=%s', url)
    macs = []
    # mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21
    for s in queryset:
        macs.append(s.mac)
    data = {
        'server_key': server_key,
        'mac[]': [macs]
        }
    log.debug('Reboot=%s, macs[]=%s', url, macs)
    log.debug('DATA=%s', data)
    try:
        response = requests.post(url, timeout=10, data=data)
        log.debug('Resposta=[%s]%s', response.status_code, response.text)
    except Exception as e:
        log.error('ERROR:%s', e)
    finally:
        log.info('Finalizado o request')


def reboot_stb(modeladmin, request, queryset):
    log.debug('Reboot')
    nbs = Nbridge.objects.filter(status=True)
    log.debug('NBS=%s', nbs)
    for s in nbs:
        log.debug('Enviando para nb=%s', s)
        thread.start_new_thread(reboot_stbs, (queryset, s))

reboot_stb.short_description = ugettext_lazy(
    'Reiniciar %(verbose_name_plural)s selecionados')


class SetTopBoxChannelInline(admin.TabularInline):
    model = models.SetTopBoxChannel
    #template = 'admin/client/edit_inline/settopboxchannel.html'


class SetTopBoxAdmin(ModelAdmin):
    search_fields = ('mac', 'serial_number', 'description', )
    list_display = (
        'serial_number', 'mac', 'description', 'online', 'ip', 'nbridge',
    )
    actions = [reboot_stb, reload_channels_stb, start_remote_debug]
    inlines = [SetTopBoxChannelInline, ]
    list_filter = ['online',]
    # list_select_related = True

    def get_readonly_fields(self, request, obj = None):
        if obj:
            return (
                'mac', 'serial_number', 'online', 'nbridge', 'ip',
            ) + self.readonly_fields
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
    #forms = GenericRelationForm()
    #model =
    pass

#class MyForm(ModelForm):
#
#    MY_CHOICES = [('green', 'green'), ('red', 'red')]
#    def __init__(self, *args, **kwargs):
#        super(MyForm, self).__init__(*args, **kwargs)
#        if self.instance.id:
#            CHOICES_INCLUDING_DB_VALUE = [(self.instance.field,)*2] + self.MY_CHOICES
#                                           self.fields['my_field'] = forms.ChoiceField(
#                                           choices=CHOICES_INCLUDING_DB_VALUE)

site.register(models.SetTopBox, SetTopBoxAdmin)
# site.register(models.SetTopBoxParameter)
site.register(models.SetTopBoxProgramSchedule)
site.register(models.SetTopBoxChannel, SetTopBoxChannelAdmin)
site.register(models.SetTopBoxConfig, SetTopBoxConfigAdmin)
site.register(models.SetTopBoxMessage, SetTopBoxMessageAdmin)
site.register(models.SetTopBoxBehaviorFlag)
