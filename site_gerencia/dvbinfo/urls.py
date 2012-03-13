#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('dvbinfo.views',
    (r'^transponders/', 'get_transponders'),
    (r'^channels/', 'get_channels'),
)
