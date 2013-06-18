#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Modulo: 
"""
__author__ = 'Sergio Cioban Filho'
__version__ = '1.0'
__date__ = '03/10/2012 06:08:10 PM'


from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, ugettext as _

import models

from monitoramento.admin_views import dashboard, channel_tree, mon_export
from device.admin import AdminServer

def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
            url(r'^dashboard/$', admin.site.admin_view(dashboard),
                name='mon_dashboard'),
            url(r'^dashboard/channel_tree_status/$',
                admin.site.admin_view(channel_tree),
                name='mon_channel_tree_status'),
            url(r'^dashboard/channel_tree/$',
                admin.site.admin_view(channel_tree), name='mon_channel_tree'),
            url(r'^dashboard/export/$', admin.site.admin_view(mon_export),
                name='mon_export'),
        )
        return my_urls + urls
    return get_urls

def test_all_servers(modeladmin, request, queryset):
    for s in queryset:
        s.connect()
        if s.status is True:
            s.auto_create_nic()

test_all_servers.short_description = ugettext_lazy(
    u'Testar %(verbose_name_plural)s selecionados')

class AdminMonServer(admin.ModelAdmin):
    readonly_fields = ('status', 'modified', 'msg',)
    list_display = ('__unicode__', 'server_type', 'status', 'msg',
        'switch_link',)
    fieldsets = (
      (None, {
        'fields': (('status', 'modified', 'msg', ),
            ('name', ),
            ('http_port',),
            ('http_username', 'http_password', ),
            ('host', 'ssh_port', ),
            ('username', 'password',),
            ('rsakey'),
        )
      }),
    )
    actions = [test_all_servers]
    #readonly_fields = ('status', 'modified', 'msg',)
    #list_display = ('__unicode__', 'server_type', 'status', 'msg',
    #    'switch_link',)
    #fieldsets = (
    #  (None, {
    #    'fields': (('status', 'modified', 'msg', ),
    #        ('server_type'),
    #        ('name', ),
    #        ('host', 'ssh_port', ),
    #        ('username', 'password',),
    #        ('rsakey'),
    #    )
    #  }),
    #)
    #actions = [test_all_servers]



admin.site.register(models.MonServer, AdminMonServer)
#admin.site.register(models.MonServer, AdminServer)

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
