#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^import_to_db/(?P<epg_source_id>\d+)/$', 'epg.views.import_to_db'),
    (r'^import_status/(?P<epg_source_id>\d+)/$', 'epg.views.get_import_current_status'),
    (r'^delete_from_db/(?P<epg_source_id>\d+)/$', 'epg.views.delete_from_db'),
    (r'^get_channels_list/$', 'epg.views.get_channels_list'),
    (r'^get_channel_info/(?P<channel_id>\d+)/$', 'epg.views.get_channel_info'),
    (r'^get_channel_programmes/(?P<channel_id>\d+)/$', 'epg.views.get_channel_programmes'),
    (r'^get_programme_info/(?P<programme_id>\d+)/$', 'epg.views.get_programme_info'),
)
