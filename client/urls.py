# -*- encoding:utf8 -*
'''
module: client.urls
@author: helber
'''

from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from . import dispatch
from .views import Auth, SetTopBoxReportView

urlpatterns = patterns('',
    #url(r'^auth/(?P<mac>[0-9A-Fa-f:]{17})/.*$', 'client.views.auth',
    #    name='client_auth'),
    url(r'^auth/$', csrf_exempt(Auth.as_view()), name='client_auth'),
    url(r'^logoff/$', 'client.views.logoff', name='client_logoff'),
    url(r'^offline/$', 'client.views.offline', name='client_offline'),
    url(r'^online/$', 'client.views.online', name='client_online'),
    url(r'^route/(?P<stbs>[^/]+)/(?P<key>\w+)/(?P<cmd>.+)$',
        'client.views.change_route', name='client_route'),
    url(r'^commands/reload_channels/(?P<stbs>[^/]+)/(?P<message>.+)',
        'client.views.reload_channels', name='client_reload_channels'),
    url(r'^nbridgedown/$', 'client.views.nbridge_down', name='client_nbridge'),
    url(r'^stbs-reports/$', SetTopBoxReportView.as_view(), name='stbs_report'),
    )
