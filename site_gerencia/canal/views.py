#!/usr/bin/env python
# -*- encoding:utf8 -*-
from base import *
from canal import models, forms
from django.core import serializers
from django.conf import settings

def index(request):
    lista =  models.Canal.objects.all()
    return render_to_response(
                              'canal/canais.html',
                              { 'canais': lista },
                              context_instance=RequestContext(request)
                              )


def add(request):
    """
    Adiciona novo canal.
    """
    if request.method == 'POST':
        # Adiciona novo canal
        form = forms.CanalForm(request.POST,request.FILES)
        if form.is_valid():
            novocanal = models.Canal()
            fcanal = forms.CanalForm(request.POST,request.FILES,instance=novocanal)
            fcanal.save()
            #request.user.message_set.create(message=_("Canal registrado com sucesso"))
            return HttpResponseRedirect(reverse('canal_get'))
        else:
            return render_to_response('canal/canaladd.html', {'form': form},
                                        context_instance=RequestContext(request))
    else:
        form = forms.CanalForm()
        return render_to_response('canal/canaladd.html', {'form': form},
                                            context_instance=RequestContext(request))

def edit(request,id):
    """
    Editação dos dados do canal.
    """
    canal = get_object_or_404(models.Canal,pk=id)
    if request.method == 'POST':
        form = forms.CanalForm(request.POST,request.FILES,instance=canal)
        #print '\n'.join(sorted(dir(request)))
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('canal_get'))
    else:
        form = forms.CanalForm(instance=canal)
    return render_to_response('canal/canaledit.html', {'form': form , 'canal':canal},
                                        context_instance=RequestContext(request))

def delete(request,id):
    """
    Remove o canal
    """
    canal = get_object_or_404(models.Canal,pk=id)
    canal.delete()
    return HttpResponseRedirect(reverse('canal_get'))



def ajaxlist(request):
    #print ('\n'.join(request))
    canais = models.Canal.objects.all()
    MEDIA_URL=getattr(settings, 'MEDIA_URL')
    # Chama o canal e pega a listagem do aplicativo canal
    js = serializers.serialize('json',canais,indent=2, use_natural_keys=True)
    return HttpResponse('{"media_url":"%s",data:%s}'%(MEDIA_URL,js))


