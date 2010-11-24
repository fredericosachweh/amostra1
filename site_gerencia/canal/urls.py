#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns,url

urlpatterns = patterns('',
    url(r'^add/$','canal.views.add', name='canal_add'),
    url(r'^delete/(?P<id>\d)$','canal.views.delete', name='canal_delete'),
    url(r'^get/$','canal.views.index', name='canal_get'),
    url(r'^edit/(?P<id>\d)$','canal.views.edit', name='canal_edit'),
    url(r'^index/$','canal.views.index',name='canal_index'),
    url(r'^canallist/$','canal.views.canallist',name='canallist'),
    url(r'^$','canal.views.index'),
    )
