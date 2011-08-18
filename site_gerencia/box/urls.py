#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from django.conf import settings

urlpatterns = patterns('',
    url(r'^index/$',      'box.views.index',          name='box_index'),
    url(r'^$',            'box.views.index'),
    url(r'^canal_list/$', 'box.views.canal_list',     name='canal_list'),
    url(r'^auth/(?P<mac>[0-9A-F:]{10,20})/.*$','box.views.auth', name='box_auth'),
    url(r'^remote_log/$',   'box.views.remote_log',   name='box_remote_log'),
    url(r'^canal_update/$', 'box.views.canal_update', name='canal_update'),
    url(r'^setup/$',        'box.views.setup',        name='setup'),
    url(r'^frontend/$',     direct_to_template, {'template': 'frontend/index.html'}),
    url(r'^frontend/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT+"/frontend/",
        }),
    )
