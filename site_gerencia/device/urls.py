#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$','device.views.home'),
    (r'^server/status/(?P<pk>\d+)/$','device.views.server_status'),
    (r'^server/interfaces/$','device.views.server_list_interfaces'),
    (r'^server/adapter/(?P<adapter_nr>\d+)/$','device.views.server_update_adapter'),
    (r'^server/dvbtuners/$','device.views.server_list_dvbadapters'),
    (r'^file/start/(?P<pk>\d+)/$', 'device.views.file_start'),
    (r'^file/stop/(?P<pk>\d+)/$', 'device.views.file_stop'),
    (r'^multicat/start/(?P<pk>\d+)/$','device.views.multicat_start'),
    (r'^multicat/stop/(?P<pk>\d+)/$','device.views.multicat_stop'),
    (r'^multicatredirect/start/(?P<pk>\d+)/$','device.views.multicat_redirect_start'),
    (r'^multicatredirect/stop/(?P<pk>\d+)/$','device.views.multicat_redirect_stop'),
    #(r'^dvbtuners/$', 'device.views.get_dvb_tuners'),
    (r'^isdbtuners/$', 'device.views.get_isdb_tuners'),
    (r'^autofilltuner/(?P<ttype>[a-z]+)/$',
        'device.views.auto_fill_tuner_form'),
)
