#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$','device.views.home'),
    (r'^server/status/(?P<pk>\d+)/$','device.views.server_status'),
    (r'^vlc/start/(?P<pk>\d+)/$','device.views.vlc_start'),
    (r'^vlc/stop/(?P<pk>\d+)/$','device.views.vlc_stop'),
    (r'^multicat/start/(?P<pk>\d+)/$','device.views.multicat_start'),
    (r'^multicat/stop/(?P<pk>\d+)/$','device.views.multicat_stop'),
    (r'^multicatredirect/start/(?P<pk>\d+)/$','device.views.multicat_redirect_start'),
    (r'^multicatredirect/stop/(?P<pk>\d+)/$','device.views.multicat_redirect_stop'),
    (r'^dvbtuners/$', 'device.views.get_dvb_tuners'),
    (r'^autofilltuner/$', 'device.views.auto_fill_tuner_form'),
#    (r'^scan_dvb/(?P<dvbid>\d+)/$','stream.views.scan_dvb'),
#    (r'^fake_scan_dvb/(?P<dvbid>\d+)/$','stream.views.fake_scan_dvb'),
#    (r'^dvb_play/(?P<streamid>\d+)/$','stream.views.dvb_play'),
#    (r'^dvb_stop/(?P<streamid>\d+)/$','stream.views.dvb_stop'),
#    (r'^tvod/$','stream.views.tvod'),
)
