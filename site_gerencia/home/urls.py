#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import handler404,handler500,patterns,url


urlpatterns = patterns('',
    (r'^$','home.views.home'),
)
