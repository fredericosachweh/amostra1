#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from django.conf import settings
import os

urlpatterns = patterns('',
    url(r'^index/$',        'box.views.index',        name='box_index'),
    url(r'^auth/(?P<mac>[0-9A-F:]{10,20})/.*$','box.views.auth', name='box_auth'),
    url(r'^programme_info/$',               'box.views.programme_info', name='programme_info'),
    url(r'^guide_programmes/$',             'box.views.guide_programmes', name='guide_programmes'),
    url(r'^guide_mount_line_of_programe/$', 'box.views.guide_mount_line_of_programe', name='guide_mount_line_of_programe'),
    url(r'^remote_log/$',                   'box.views.remote_log',   name='box_remote_log'),
    url(r'^setup/$',                        'box.views.setup',        name='setup'),
    url(r'^ping$',          'box.views.ping',         name='ping'),
    url(r'^debug/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.dirname(settings.PROJECT_ROOT_PATH)+"/frontend/src/",
        }),
    url(r'^doc/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.dirname(settings.PROJECT_ROOT_PATH)+"/frontend/doc/",
        }),
    url(r'^$',     direct_to_template, {'template': 'box/index.html'}),
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.dirname(settings.PROJECT_ROOT_PATH)+"/frontend/dist/",
        }),
    )