#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$','device.views.home'),
    (r'^ssh_status/(?P<pk>\d+)/$','device.views.ssh_status'),
    (r'^vlc/start/(?P<pk>\d+)/$','device.views.vlc_start'),
    (r'^vlc/stop/(?P<pk>\d+)/$','device.views.vlc_stop'),
#    (r'^scan_dvb/(?P<dvbid>\d+)/$','stream.views.scan_dvb'),
#    (r'^fake_scan_dvb/(?P<dvbid>\d+)/$','stream.views.fake_scan_dvb'),
#    (r'^dvb_play/(?P<streamid>\d+)/$','stream.views.dvb_play'),
#    (r'^dvb_stop/(?P<streamid>\d+)/$','stream.views.dvb_stop'),
#    (r'^tvod/$','stream.views.tvod'),
)
