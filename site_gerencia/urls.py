#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *
from settings import MEDIA_ROOT


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^site_gerencia/', include('site_gerencia.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    # Midias estaticas
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    # Configuração de canais
    (r'^canal/',include('site_gerencia.canal.urls')),
)
