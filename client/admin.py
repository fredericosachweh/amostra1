# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
import thread
import requests
from django.contrib.admin import site, ModelAdmin
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy
from django.conf import settings
server_key = settings.NBRIDGE_SERVER_KEY
from . import models, tasks
from nbridge.models import Nbridge
from log.models import TaskLog

log = logging.getLogger('client')


def reload_channels_stb(modeladmin, request, queryset):
    message='Lista de canais atualizada'
    pks_list = queryset.values_list('pk', flat=True)
    task = TaskLog.objects.create_or_alert(
        'reload-channels', pks_list, request.user)
    if task:
        tasks.reload_channels.delay(pks_list, message, task.id, channel=False)
        messages.success(request, 'Atualizando lista de canais.')
    else:
        messages.error(request, 'Atualizando lista já está sendo atualizada.')
    

reload_channels_stb.short_description = ugettext_lazy(
    'Recarregar canais para %(verbose_name_plural)s selecionados')


def start_remote_debug(modeladmin, request, queryset):
    for s in queryset:
        s.remote_debug()

start_remote_debug.short_description = ugettext_lazy(
    'DEBUG %(verbose_name_plural)s selecionados')


def reboot_stb(modeladmin, request, queryset):
    pks_list = queryset.values_list('pk', flat=True)
    task = TaskLog.objects.create_or_alert(
        'reboot-stbs', pks_list, request.user)
    if task:
        tasks.reboot_stbs.delay(pks_list, task.id)
        messages.success(request, 'Reiniciando SetTopBoxes.')
    else:
        messages.error(request, 'SetTopBoxes já estão sendo reiniciados.')

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
    list_filter = ['online',]

    def get_readonly_fields(self, request, obj = None):
        if obj:
            return (
                'mac', 'serial_number', 'online', 'nbridge', 'ip',
            ) + self.readonly_fields
        else:
            return (
                'online', 'nbridge', 'ip',
            ) + self.readonly_fields
        return self.readonly_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [SetTopBoxChannelInline, ]
        return super(SetTopBoxAdmin, self).change_view(request, object_id)


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
