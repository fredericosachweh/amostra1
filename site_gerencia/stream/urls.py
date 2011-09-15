#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$','stream.views.home'),
    (r'^play/(?P<streamid>\d+)/$','stream.views.play'),
    (r'^stop/(?P<streamid>\d+)/$','stream.views.stop'),
)
