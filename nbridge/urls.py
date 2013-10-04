# -*- encoding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('', 
    (r'status/(?P<action>.*)/(?P<pk>\d+)/$', 'nbridge.views.status_switchlink')
)



