#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from django.conf import settings
import os

urlpatterns = patterns('',
    url(r'^index/$',        'box.views.index',        name='box_index'),
#    url(r'^$',              'box.views.index'),
    url(r'^auth/(?P<mac>[0-9A-F:]{10,20})/.*$','box.views.auth', name='box_auth'),
    url(r'^canal_list/$',            'box.views.canal_list',   name='canal_list'),
    url(r'^programme_info/$',        'box.views.programme_info', name='programme_info'),
    url(r'^guide_programmes/$',      'box.views.guide_programmes', name='guide_programmes'),
    url(r'^guide_programmes_list/$', 'box.views.guide_programmes_list', name='guide_programmes_list'),
    url(r'^channel_programme_info/$', 'box.views.channel_programme_info', name='channel_programme_info'),
    url(r'^remote_log/$',            'box.views.remote_log',   name='box_remote_log'),
    url(r'^canal_update/$',          'box.views.canal_update', name='canal_update'),
    url(r'^setup/$',                 'box.views.setup',        name='setup'),
    
    url(r'^ping$',          'box.views.ping',         name='ping'),
    
    url(r'^debug/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.dirname(settings.PROJECT_ROOT_PATH)+"/frontend/src/",
        }),
    url(r'^docs/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.dirname(settings.PROJECT_ROOT_PATH)+"/frontend/docs/",
        }),
    url(r'^$',     direct_to_template, {'template': 'box/index.html'}),
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.dirname(settings.PROJECT_ROOT_PATH)+"/frontend/dist/",
        }),
    )
