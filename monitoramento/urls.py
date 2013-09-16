#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Modulo: 
"""
__author__ = 'Sergio Cioban Filho'
__version__ = '1.0'
__date__ = '14/06/2013 09:45:09 AM'


from django.conf.urls import patterns
urlpatterns = patterns('',
    (r'^monserver/status/(?P<pk>\d+)/$',
     'monitoramento.views.monserver_status'),
)
