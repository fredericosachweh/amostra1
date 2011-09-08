# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from stream.player import Player

from models import Stream

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def play(request,stream_id=None):
    stream = get_object_or_404(Stream,id=stream_id)
    p = Player()
    proc = p.play_stream(stream)
    proc = None
    return HttpResponseRedirect(reverse('admin:stream_stream_changelist'))

def stop(request,stream_id=None):
    stream = get_object_or_404(Stream,id=stream_id)
    p = Player()
    p.stop_stream(stream)
    return HttpResponseRedirect(reverse('admin:stream_stream_changelist'))
