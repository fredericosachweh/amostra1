#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns,url,handler404,handler500

#from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$','log.views.index'),
    )
