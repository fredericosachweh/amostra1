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

from monitoramento.admin_views import dashboard, channel_tree, mon_export

def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
            url(r'^dashboard/$', admin.site.admin_view(dashboard),
                name='mon_dashboard'),
            url(r'^dashboard/channel_tree/$',
                admin.site.admin_view(channel_tree), name='mon_channel_tree'),
            url(r'^dashboard/export/$', admin.site.admin_view(mon_export),
                name='mon_export'),
        )
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
