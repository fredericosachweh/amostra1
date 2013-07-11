# -*- encoding:utf8 -*
'''
module: client.urls
@author: helber
'''
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from views import Auth

urlpatterns = patterns('',
    #url(r'^auth/(?P<mac>[0-9A-Fa-f:]{17})/.*$', 'client.views.auth',
    #    name='client_auth'),
    url(r'^auth/$', csrf_exempt(Auth.as_view()), name='client_auth'),
    url(r'^logoff/$', 'client.views.logoff', name='client_logoff'),
    )
