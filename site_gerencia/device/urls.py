#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$','device.views.home'),
    (r'^server/status/(?P<pk>\d+)/$','device.views.server_status'),
    (r'^server/interfaces/$','device.views.server_list_interfaces'),
    (r'^server/adapter/(?P<adapter_nr>\d+)/$','device.views.server_update_adapter'),
    (r'^server/dvbtuners/$','device.views.server_list_dvbadapters'),
    (r'^server/isdbtuners/$','device.views.server_available_isdbtuners'),
    # DvbTuner
    (r'^dvbtuner/start/(?P<pk>\d+)/$','device.views.dvbtuner_start'),
    (r'^dvbtuner/stop/(?P<pk>\d+)/$','device.views.dvbtuner_stop'),
    # IsdbTuner
    (r'^isdbtuner/start/(?P<pk>\d+)/$','device.views.isdbtuner_start'),
    (r'^isdbtuner/stop/(?P<pk>\d+)/$','device.views.isdbtuner_stop'),
    # UnicastInput
    (r'^unicastinput/start/(?P<pk>\d+)/$','device.views.unicastinput_start'),
    (r'^unicastinput/stop/(?P<pk>\d+)/$','device.views.unicastinput_stop'),
    # MulticastInput
    (r'^multicastinput/start/(?P<pk>\d+)/$','device.views.multicastinput_start'),
    (r'^multicastinput/stop/(?P<pk>\d+)/$','device.views.multicastinput_stop'),
    
    (r'^file/start/(?P<pk>\d+)/$', 'device.views.file_start'),
    (r'^file/stop/(?P<pk>\d+)/$', 'device.views.file_stop'),
    (r'^multicat/start/(?P<pk>\d+)/$','device.views.multicat_start'),
    (r'^multicat/stop/(?P<pk>\d+)/$','device.views.multicat_stop'),
    (r'^multicatredirect/start/(?P<pk>\d+)/$','device.views.multicat_redirect_start'),
    (r'^multicatredirect/stop/(?P<pk>\d+)/$','device.views.multicat_redirect_stop'),
    (r'^autofilltuner/(?P<ttype>[a-z]+)/$',
        'device.views.auto_fill_tuner_form'),
)
