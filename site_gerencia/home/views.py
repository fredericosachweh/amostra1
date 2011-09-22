#!/usr/bin/env python
#encoding:utf8

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def home(request):
    return render_to_response('index.html', {},\
        context_instance=RequestContext(request))
