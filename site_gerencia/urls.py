#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import patterns, include, url, handler404, handler500
from django.views.generic.simple import direct_to_template
#from django.conf.urls.defaults import *

from settings import MEDIA_ROOT, STATIC_ROOT
#import canal,box

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^tv/accounts/login/$', 'django.contrib.auth.views.login', name='sys_login'),
    url(r'^tv/accounts/logout/$', 'django.contrib.auth.views.logout', name='sys_logout'),

    # Uncomment the next line to enable the admin:
    (r'^tv/administracao/', include(admin.site.urls)),
    # Midias estaticas
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    # Configuração de canais
    (r'^tv/canal/',include('canal.urls')),
    # Interface dos setupbox
    (r'^tv/box/',include('box.urls')),
    # Streams de multicats
    (r'^tv/stream/',include('stream.urls')),
    # Página inicial
    (r'^tv/$',direct_to_template,{'template':'index.html'} ),
)

