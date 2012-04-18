#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'device.views.home'),
    (r'^server/status/(?P<pk>\d+)/$', 'device.views.server_status'),
    (r'^server/interfaces/$', 'device.views.server_list_interfaces'),
    (r'^file/start/(?P<pk>\d+)/$', 'device.views.file_start'),
    (r'^file/stop/(?P<pk>\d+)/$', 'device.views.file_stop'),
    (r'^dvbtuners/$', 'device.views.get_dvb_tuners'),
    (r'^isdbtuners/$', 'device.views.get_isdb_tuners'),
    (r'^autofilltuner/(?P<ttype>[a-z]+)/$',
        'device.views.auto_fill_tuner_form'),
)
