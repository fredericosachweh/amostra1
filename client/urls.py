# -*- encoding:utf8 -*
'''
module: client.urls
@author: helber
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^auth/(?P<mac>[0-9A-Fa-f:]{17})/.*$', 'client.views.auth',
        name='client_auth'),
    )
