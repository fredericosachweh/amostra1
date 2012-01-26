#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^import/(?P<arquivo_epg_id>\d+)/$', 'epg.views.import_to_db'),
    (r'^import_status/(?P<arquivo_epg_id>\d+)/$', 'epg.views.get_import_current_status'),
)
