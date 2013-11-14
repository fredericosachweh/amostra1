#!/usr/bin/env python
# -*- encoding:utf8 -*-
from django.conf.urls import patterns, url, handler404, handler500

#from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^log/$','tools.views.log'),
    url(r'^date/$','tools.views.date'),
    url(r'^network/$','tools.views.network'),
    )
