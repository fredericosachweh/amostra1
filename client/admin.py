# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from django.core.cache import cache
from django.contrib.admin import site, ModelAdmin
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy
from django.conf import settings
server_key = settings.NBRIDGE_SERVER_KEY
from . import models, tasks
from log.models import TaskLog
from log.views import create_cache_log

log = logging.getLogger('client')


def reload_channels_stb(modeladmin, request, queryset):
    message = 'Lista de canais atualizada'
    pks_list = queryset.values_list('pk', flat=True)
    task_log = TaskLog.objects.create_or_alert(
        'reload-channels', pks_list, request.user)
    if task_log:
        task = tasks.reload_channels.delay(pks_list, message, task_log.id, channel=False)
        create_cache_log(task.task_id, task_log.id)
        messages.success(request, 'Atualizando lista de canais.')
    else:
        messages.error(request, 'Lista de canais já está sendo atualizada.')

reload_channels_stb.short_description = ugettext_lazy(
    'Recarregar canais para %(verbose_name_plural)s selecionados')


def reload_frontend_stbs(modeladmin, request, queryset):
    pks_list = queryset.values_list('pk', flat=True)
    task_log = TaskLog.objects.create_or_alert(
        'reload-frontend-stbs', pks_list, request.user)
    if task_log:
        task = tasks.reload_frontend_stbs.delay(pks_list, task_log.id)
        create_cache_log(task.task_id, task_log.id)
        messages.success(request, 'Reiniciando frontend dos SetTopBoxes.')
    else:
        messages.error(request, u'Frontend dos'
                       'SetTopBoxes já estão sendo reiniciados.')
reload_frontend_stbs.short_description = ugettext_lazy(
    'Reiniciando frontend para %(verbose_name_plural)s selecionados')


def accept_recorder(modeladmin, request, queryset):
    message = u'Liberar canais para acessar conteúdo gravado concluído.'
    pks_list = queryset.values_list('pk', flat=True)
    task_log = TaskLog.objects.create_or_alert(
        'accept-recorder', pks_list, request.user)
    if task_log:
        task = tasks.accept_recorder.delay(pks_list, message, task_log.id, channel=False)
        create_cache_log(task.task_id, task_log.id)
        messages.success(request, u'Atualizando canais para acessar '
                         'conteúdo gravado.')
    else:
        messages.error(request, u'Liberar canais para acessar conteúdo'
                       'gravado já está em execução.')
accept_recorder.short_description = ugettext_lazy(
    u'Liberar canais para acessar conteúdo gravado.')


def refuse_recorder(modeladmin, request, queryset):
    message = u'Bloquear canais para acessar conteúdo gravado concluído.'
    pks_list = queryset.values_list('pk', flat=True)
    task_log = TaskLog.objects.create_or_alert(
        'refuse-recorder', pks_list, request.user)
    if task_log:
        task = tasks.refuse_recorder.delay(pks_list, message, task_log.id, channel=False)
        create_cache_log(task.task_id, task_log.id)
        messages.success(request, u'Atualizando canais para bloquear '
                         'conteúdo gravado.')
    else:
        messages.error(request, u'Bloquear canais para acessar conteúdo'
                       'gravado já está em execução.')
refuse_recorder.short_description = ugettext_lazy(
    u'Bloquear canais para acessar conteúdo gravado.')


def start_remote_debug(modeladmin, request, queryset):
    for s in queryset:
        s.remote_debug()

start_remote_debug.short_description = ugettext_lazy(
    'DEBUG %(verbose_name_plural)s selecionados')


def reboot_stb(modeladmin, request, queryset):
    pks_list = queryset.values_list('pk', flat=True)
    task_log = TaskLog.objects.create_or_alert(
        'reboot-stbs', pks_list, request.user)
    if task_log:
        task = tasks.reboot_stbs.delay(pks_list, task_log.id)
        create_cache_log(task.task_id, task_log.id)
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
    actions = [reboot_stb, reload_channels_stb, start_remote_debug,
               accept_recorder, refuse_recorder, reload_frontend_stbs]
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
