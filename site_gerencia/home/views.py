#!/usr/bin/env python
#encoding:utf8

from django.http import HttpResponse

def home(request):
    return HttpResponse('Página inicial')
