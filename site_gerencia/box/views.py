#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""Visualização e entrega de json para SetupBox"""

from __future__       import print_function
import sys

from django.http      import HttpResponse
from django.shortcuts import render_to_response
from django.template  import RequestContext

from canal.models     import Canal

from django.conf      import settings
from django.core      import serializers

def index(request):
    """
    Imprime informações no console e exibe requsição do box pro setupbox
    """
    #print(request.COOKIES)
    #print(dir(request.META))
    #print(' | '.join(request.META))
    #print('---->IP:',request.META['REMOTE_ADDR'],end='|',sep='=')
    stress = request.GET.get('stress')
    #print('IP=%s'%request.META['REMOTE_ADDR'])
    #print('IP: %s %s' %(request.REMOTE_ADDR,request.REMOTE_HOST))
    return render_to_response(
                              'box/index.html',
                              { 'stress':stress },
                              context_instance=RequestContext(request)
                              )

def setup(request):
    """Ambiente base de setup"""
    return render_to_response(
                              'box/setup.html',
                              {},
                              context_instance=RequestContext(request)
                              )


def auth(request, mac = None):
    """Realiza a autenticação do setupbox atravéz de seu endereço MAC"""
    #print('MAC=%s'%mac)
    return HttpResponse('{"MAC":"%s"}'%mac)

def remote_log(request):
    """
    Exibe log no console
    """
    #print(dir(request))
    #print('----->ERROR IP: %s' %request.META.get('REMOTE_ADDR'))
    #print('message',request.POST.get('body'))
    #print('stack',request.POST.get('stack'))
    return HttpResponse('{"success":"true"}')

def canal_list(request):
    """
    Usado pelo setupbox para pegar a lista de canais
    """
    canais = Canal.objects.all().order_by('numero')
    # Chama o canal e pega a listagem do aplicativo canal
    json = serializers.serialize('json', canais, indent=2, use_natural_keys = True)
    return HttpResponse(json)

def canal_update(request):
    """Retorna a data de atualização mais recente da lista de canais"""
    #print('---->IP:',request.META['REMOTE_ADDR'],end=' ')
    #sys.stdout.flush()
    #print('META',' | '.join(request.META))
    atual = Canal.objects.all().order_by('-atualizado')[0]
    #return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.strftime('%Y-%m-%dT%H:%M:%S')))
    #return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.isoformat()))
    return HttpResponse('{"atualizado":"%s"}'%(atual.atualizado.ctime()))

def ping(request):
    """ Responde true """
    print('--> Ping from %s' % (request.META['REMOTE_ADDR']))
    try:
        import Image
    except:
        from PIL import Image
    image = Image.new("RGB", (1, 1), "black")
    
    response = HttpResponse(mimetype='image/png')
    image.save(response, "PNG")
    #return HttpResponse() # Remova o comentário para emular servidor sem conexão
    return response






