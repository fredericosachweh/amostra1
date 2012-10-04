#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Modulo: 
"""
__author__ = 'Sergio Cioban Filho'
__version__ = '1.0'
__date__ = '03/10/2012 06:08:10 PM'


from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def my_view(request):
    #return HttpResponse("Hello!")
    resposta = render_to_response("admin/mon.html",
        { 'PAGE_NAME': 'Inscerver', }, context_instance=RequestContext(request))
    return resposta
    #return render_to_response('admin/%s/questaorespondida_list.html' % app_label,
    #                              {'objetos': objetos},
    #                              context_instance=template.RequestContext(request))


def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
            (r'^mon/$', admin.site.admin_view(my_view))
        )
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
