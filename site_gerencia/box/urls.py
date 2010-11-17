#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns,url

urlpatterns = patterns('',
    url(r'^index/$','box.views.index',name='box_index'),
    url(r'^$','box.views.index'),
    )
