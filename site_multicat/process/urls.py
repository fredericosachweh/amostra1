#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$','process.views.home'),
    url(r'^list/$','process.views.process_list'),
    url(r'^channel/(?P<id>\d)$','process.views.channel_edit'),
    url(r'play/(?P<stream_id>\d)$','process.views.play',name='play_stream'),
    url(r'stop/(?P<stream_id>\d)$','process.views.stop',name='stop_stream'),
)