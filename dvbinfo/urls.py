#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('dvbinfo.views',
    (r'^transponders/$', 'get_transponders'),
    (r'^channels/dvbs/$', 'get_dvbs_channels'),
    (r'^channels/isdb/$', 'get_isdb_channels'),
    (r'^channel/isdb/$', 'get_isdb_channel'),
    (r'^cities/$', 'get_cities'),
)
