#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    # Channel
    (r'^channel/start/(?P<pk>\d+)/$', 'tv.views.channel_switchlink',
     {'action': 'start'}, 'channel_start'),
    (r'^channel/stop/(?P<pk>\d+)/$', 'tv.views.channel_switchlink',
     {'action': 'stop'}, 'channel_stop'),
    (r'^input/interfaces/$','tv.views.input_list_interfaces'),

)
