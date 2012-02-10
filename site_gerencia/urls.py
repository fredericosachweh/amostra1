#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns, include, url, handler404, handler500
from django.views.generic.simple import direct_to_template
#from django.conf.urls.defaults import *

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^%saccounts/login/$'%settings.ROOT_URL, 'django.contrib.auth.views.login', name='sys_login'),
    url(r'^%saccounts/logout/$'%settings.ROOT_URL, 'django.contrib.auth.views.logout', name='sys_logout'),

    # Uncomment the next line to enable the admin:
    (r'^%sadministracao/'%settings.ROOT_URL, include(admin.site.urls)),
    # Midias estaticas
    (r'^%smedia/(?P<path>.*)$'%settings.ROOT_URL, 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^%sstatic/(?P<path>.*)$'%settings.ROOT_URL, 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    # Configuração de canais
    (r'^%scanal/'%settings.ROOT_URL,include('canal.urls')),
    # Interface dos setupbox
    (r'^%sbox/'%settings.ROOT_URL,include('box.urls')),
    # Streams de multicats
    (r'^%sstream/'%settings.ROOT_URL,include('stream.urls')),
    # EPG
    (r'^%sepg/'%settings.ROOT_URL,include('epg.urls')),
    # REST interface for the EPG
    (r'^%sapi/'%settings.ROOT_URL, include('api.urls')),
    # Página inicial
    #(r'^%s$'%settings.ROOT_URL,direct_to_template,{'template':'index.html'} ),
    (r'^%s$'%settings.ROOT_URL,include('home.urls')),
    
    #(r'^dowser/', include('django_dowser.urls')),
)

