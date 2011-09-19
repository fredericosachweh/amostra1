
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
#from stream.player import Player
from models import Stream,DVBSource

from models import Stream

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def play(request,streamid=None):
    stream = get_object_or_404(Stream,id=streamid)
    stream.play()
    return HttpResponseRedirect(reverse('admin:stream_stream_changelist'))

def stop(request,streamid=None):
    stream = get_object_or_404(Stream,id=streamid)
    stream.stop()
    return HttpResponseRedirect(reverse('admin:stream_stream_changelist'))

def scan_dvb(request,dvbid=None):
    dvb = get_object_or_404(DVBSource,id=dvbid)
    import simplejson
    canais = dvb.scan_channels()
    enc = simplejson.encoder.JSONEncoder()
    resposta = enc.encode(canais)
    #print(resposta)
    return HttpResponse(resposta,mimetype='application/javascript')