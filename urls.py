#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.views.generic import TemplateView
from django.utils.importlib import import_module

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^%saccounts/login/$' % settings.ROOT_URL,
        'django.contrib.auth.views.login', name='sys_login'),
    url(r'^%saccounts/logout/$' % settings.ROOT_URL,
        'django.contrib.auth.views.logout', name='sys_logout'),
    # Uncomment the next line to enable the admin:
    (r'^%sadministracao/' % settings.ROOT_URL, include(admin.site.urls)),
    # Midias estaticas
    (r'^%smedia/(?P<path>.*)$' % settings.ROOT_URL,
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    (r'^%sstatic/(?P<path>.*)$' % settings.ROOT_URL,
     'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    # Configuração de canais
    (r'^%stv/' % settings.ROOT_URL, include('tv.urls')),
    # Interface dos setupbox
    (r'^%sbox/' % settings.ROOT_URL, include('box.urls')),
    # EPG
    (r'^%sepg/' % settings.ROOT_URL, include('epg.urls')),
    # tools
    (r'^%stools/' % settings.ROOT_URL, include('tools.urls')),
    # DVBInfo
    (r'^%sdvbinfo/' % settings.ROOT_URL, include('dvbinfo.urls')),
    # Devices em servidores
    (r'^%sdevice/' % settings.ROOT_URL, include('device.urls')),
    (r'^%smonitoramento/' % settings.ROOT_URL, include('monitoramento.urls')),
    (r'^%sclient/' % settings.ROOT_URL, include('client.urls')),
    (r'^%ssettings/' % settings.ROOT_URL,
     include('dbsettings.urls')),
    # Página inicial
    (r'^%s$' % settings.ROOT_URL,
     TemplateView.as_view(template_name='index.html')),
)

# This is to auto import urls from APIs. RESTful interface
for app in settings.INSTALLED_APPS:
    if app.startswith('django.') is False:
        try:
            api = import_module('%s.api' % app)
            urls = url(r'^%sapi/%s/' % (settings.ROOT_URL, app),
                include(api.api.urls, namespace=app, app_name=app))
            #urlpatterns.insert(0, urls)
            urlpatterns += patterns('', urls)
        except ImportError as e:
            pass
