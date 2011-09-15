# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from stream.player import Player

from models import Stream

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def play(request,streamid=None):
    stream = get_object_or_404(Stream,id=streamid)
    p = Player()
    pid = p.play_stream(stream)
    stream.pid = pid
    stream.save()
    return HttpResponseRedirect(reverse('admin:stream_stream_changelist'))

def stop(request,streamid=None):
    stream = get_object_or_404(Stream,id=streamid)
    p = Player()
    p.stop_stream(stream)
    return HttpResponseRedirect(reverse('admin:stream_stream_changelist'))
