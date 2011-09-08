#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$','stream.views.home'),
    url(r'play/(?P<stream_id>\d)$','stream.views.play',name='play_stream'),
    url(r'stop/(?P<stream_id>\d)$','stream.views.stop',name='stop_stream'),
)