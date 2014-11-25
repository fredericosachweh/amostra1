#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Channel
from django.db import models

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy


def start_channels_action(modeladmin, request, queryset):
    for channel in queryset:
        channel.start()

start_channels_action.short_description = ugettext_lazy(
    'Iniciar %(verbose_name_plural)s selecionados')


def stop_channels_action(modeladmin, request, queryset):
    for channel in queryset:
        channel.stop()

stop_channels_action.short_description = ugettext_lazy(
    'Parar %(verbose_name_plural)s selecionados')


class AdminImageWidget(AdminFileWidget):
    """
    Formata renderização de imagem no HTML
    """
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                '<a href="%s" target="_blank"><img src="%s" alt="%s" /></a>%s'
                % (
                    image_url,
                    image_url.replace('original', 'thumb'),
                    file_name,
                    ('Change:')
                )
            )
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(''.join(output))


class ChannelAdmin(admin.ModelAdmin):
    """
    Define modelo administrativo do Canal
    """
    fieldsets = ((None, {
        'fields': (
            ('number', 'name', 'channelid', 'enabled'),
            'description', 'image', 'buffer_size',
                ('source'),
            ),
        }),)
    #readonly_fields = ('thumb',)
    #filter_horizontal = ('programa',)
    #fields = ('numero','nome','descricao','logo','sigla','source', )
    list_display = ('image_thum', 'number', 'name', 'channelid', 'source',
        'buffer_size', 'enabled', 'switch_link')
    list_display_links = ('image_thum',)
    list_editable = ('number', 'source', 'name', 'enabled',
        'buffer_size',)
    save_as = True
    list_per_page = 10
    search_fields = ['name', 'channelid']
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}
    actions = [start_channels_action, stop_channels_action]

    ## Colocando imegem dentro do formulario
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'image':
            kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ChannelAdmin, self).formfield_for_dbfield(db_field,
            **kwargs)

admin.site.register(Channel, ChannelAdmin)
