#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from canal.models import Canal

from django.conf import settings
from django.core import serializers

def index(request):
    #print(request.COOKIES)
    #print(dir(request.META))
    #print(' | '.join(request.META))
    print('IP=%s',request.META['REMOTE_ADDR'])
    #print('IP: %s %s' %(request.REMOTE_ADDR,request.REMOTE_HOST))
    return render_to_response(
                              'box/index.html',
                              { 'info':'info' },
                              context_instance=RequestContext(request)
                              )


def auth(request,mac=None):
    """Realiza a autenticação do setupbox atravéz de seu endereço MAC"""
    #print('MAC=%s'%mac)
    return HttpResponse('{"MAC":"%s"}'%mac)

def remote_log(request):
    #print(dir(request))
    print('message',request.POST['body'])
    print('stack',request.POST['stack'])
    #print('POST',request.POST)
    #print('GET',' | '.join(request.GET))
    return HttpResponse('{"success":"true"}')

def canal_list(request):
    """
    Usado pelo setupbox para pegar a lista de canais
    """
    canais = Canal.objects.all().order_by('numero')
    MEDIA_URL=getattr(settings, 'MEDIA_URL')
    # Chama o canal e pega a listagem do aplicativo canal
    js = serializers.serialize('json',canais,indent=2, use_natural_keys=True)
    return HttpResponse('{"media_url":"%s","data":%s}'%(MEDIA_URL,js))

def canal_update(request):
    """Retorna a data de atualização mais recente da lista de canais"""
    print('IP: %s' %request.META['REMOTE_ADDR'])
    #print(request.REMOTE_ADDR)
    #print('META',' | '.join(request.META))
    atual = Canal.objects.all().order_by('-atualizado')[0]
    #return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.strftime('%Y-%m-%dT%H:%M:%S')))
    #return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.isoformat()))
    return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.ctime()))

