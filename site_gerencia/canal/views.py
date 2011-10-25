#!/usr/bin/env python
# -*- encoding:utf8 -*-


#from base import *
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

from canal import models, forms

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
    form = forms.CanalForm(request.POST or None,request.FILES or None)
    if request.method == 'POST':
        # Adiciona novo canal
        if form.is_valid():
            novocanal = models.Canal()
            fcanal = forms.CanalForm(
                request.POST,
                request.FILES,
                instance=novocanal)
            fcanal.save()
            return HttpResponseRedirect(reverse('canal_index'))
        else:
            return render_to_response('canal/canaladd.html',
                {'form': form},
                context_instance=RequestContext(request))
    else:
        return render_to_response('canal/canaladd.html',
            {'form': form},
            context_instance=RequestContext(request))

def edit(request,id):
    """
    Editação dos dados do canal.
    """
    canal = get_object_or_404(models.Canal,pk=id)
    if request.method == 'POST':
        form = forms.CanalForm(request.POST,request.FILES,instance=canal)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('canal_index'))
    else:
        form = forms.CanalForm(instance=canal)
    return render_to_response(
        'canal/canaledit.html',
        {'form': form , 'canal':canal},
        context_instance=RequestContext(request))

def delete(request,id):
    """
    Remove o canal
    """
    canal = get_object_or_404(models.Canal,pk=id)
    canal.delete()
    return HttpResponseRedirect(reverse('canal_index'))



