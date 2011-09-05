# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from stream.player import Player

from models import Stream

def home(request):
    func, args, kwargs = resolve('/process/play/1')
    print(func, args, kwargs)
    play = reverse('process.views.play',kwargs=kwargs)
    #{'stream_id': '1'}
    print(play)
    return HttpResponse('Na raiz do sistema')

def process_list(request):
    p = Player()
    p.list_running()
    return HttpResponse('Listagem')

def channel_edit(request,id=None):
    #channel = get_object_or_404(Channel,id=id)
    #return HttpResponse('Editando canal %d (%s - %s)'%(channel.id,channel.name,channel.origin_ip))
    return HttpResponse('Edit')

def play(request,stream_id=None):
    stream = get_object_or_404(Stream,id=stream_id)
    p = Player()
    p.play_stream(stream)
    #print('Stream=%s'%stream)
    return HttpResponseRedirect('/admin/process/stream/')
    #return HttpResponse('Tocando canal:%s'%stream)

def stop(request,stream_id=None):
    stream = get_object_or_404(Stream,id=stream_id)
    p = Player()
    p.stop_stream(stream)
    return HttpResponseRedirect('/admin/process/stream/')
    #return HttpResponse('Parando canal:%s'%stream)