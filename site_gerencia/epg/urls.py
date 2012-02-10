#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^import_to_db/(?P<epg_source_id>\d+)/$', 'epg.views.import_to_db'),
    (r'^import_status/(?P<epg_source_id>\d+)/$', 'epg.views.get_import_current_status'),
    (r'^delete_from_db/(?P<epg_source_id>\d+)/$', 'epg.views.delete_from_db'),
)
