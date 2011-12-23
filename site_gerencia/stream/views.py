
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
#from stream.player import Player
from models import Stream,DVBSource

#from models import Stream

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

def fake_scan_dvb(request,dvbid=None):
    import simplejson
    if dvbid == 1:
        canais = {'program': '1', 'pid': '80'}
    else:
        canais = {'program': '1', 'pid': '32'}, {'program': '2', 'pid': '259'}
    enc = simplejson.encoder.JSONEncoder()
    resposta = enc.encode(canais)
    return HttpResponse(resposta,mimetype='application/javascript')

def dvb_play(request,streamid=None):
    stream = get_object_or_404(DVBSource,id=streamid)
    stream.play()
    return HttpResponseRedirect(reverse('admin:stream_dvbsource_changelist'))

def dvb_stop(request,streamid=None):
    stream = get_object_or_404(DVBSource,id=streamid)
    stream.stop()
    return HttpResponseRedirect(reverse('admin:stream_dvbsource_changelist'))


def tvod(request):
    from player import Player
    from django.conf import settings
    import os
    ip = request.META.get('REMOTE_ADDR')
    seek = request.GET.get('seek')
    channel_number = request.GET.get('channel')
    channel = '%s/ch_%s' %(settings.CHANNEL_RECORD_DIR,channel_number)
    action = request.GET.get('action')
    # Grava:
    # multicat -r 97200000000 -u @239.0.1.1:10000 /ldslsdld/dsasd/ch_3
    # Roda unicast 5 min. 
    # multicat -U -k -$((60*5*27000000)) /ldslsdld/dsasd/ch_3 192.168.0.244:5000
    if seek:
        seek = int(seek)
    else:
        seek =  60*5
    port = 12000
    if action == 'stop':
        p = Player()
        p.direct_stop(ip)
        resposta = '{"status":"OK","command":"stop"}'
        return HttpResponse(resposta,mimetype='application/javascript')
    if os.path.exists(channel) is False:
        resposta = '{"status":"ERROR","message":"channel record %s does not existis":"path":"%s"}' %(channel_number,channel)
        return HttpResponse(resposta,mimetype='application/javascript')
    p = Player()
    pid = p.direct_play(channel, ip, port, seek)
    resposta = '{"status":"OK","PID":"%s","seek":%s,"channel_path":"%s","destination":"%s"}' %(pid,seek,channel,'%s:%d'%(ip,port))
    return HttpResponse(resposta,mimetype='application/javascript')
    


