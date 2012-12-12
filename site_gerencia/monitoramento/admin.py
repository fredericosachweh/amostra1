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

from monitoramento.admin_views import mon_list

def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
            url(r'^mon/$', admin.site.admin_view(mon_list), name='monitor')
        )
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
