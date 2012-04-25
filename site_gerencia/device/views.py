# -*- encoding:utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, \
                        HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response, render
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
import models
import forms
import logging


def home(request):
    return HttpResponseRedirect(reverse('admin:index'))


def server_status(request, pk=None):
    server = get_object_or_404(models.Server, id=pk)
    server.connect()
    log = logging.getLogger('device.view')
    log.debug('server_status(pk=%s)', pk)
    if server.status is False:
        log.error(u'Cant connect with server:(%s) %s:%d %s',
            server, server.host, server.ssh_port, server.msg)
    else:
        server.auto_create_nic()
    log.info('Server:%s [%s]', server, server.status)
    log.info('server_status(pk=%s)', pk)
    return HttpResponseRedirect(reverse('admin:device_server_changelist'))


def server_list_interfaces(request):
    log = logging.getLogger('device.view')
    pk = request.GET.get('server')
    log.debug('Server com pk=%s', pk)
    server = get_object_or_404(models.Server, id=pk)
    log.info('Listing NICs from server (pk=%s)', pk)
    response = '<option selected="selected" value="">---------</option>'
    for i in models.NIC.objects.filter(server=server):
        response += ('<option value="%s">%s - %s</option>' % (i.pk,
            i.name, i.ipv4))
    return HttpResponse(response)

def server_update_adapter(request, adapter_nr=None):
    # Identify server by its IP
    remote_addr =  request.META.get('REMOTE_ADDR', None)
    server = get_object_or_404(models.Server, host=remote_addr)
    if request.method == 'POST':
        try:
            adapter = models.DigitalTunerHardware.objects.get(server=server,
                                                        adapter_nr=adapter_nr)
        except models.DigitalTunerHardware.DoesNotExist:
            adapter = models.DigitalTunerHardware(server=server,
                                                        adapter_nr=adapter_nr)
        adapter.grab_info()
        adapter.save()
    elif request.method == 'DELETE':
        adapter = get_object_or_404(models.DigitalTunerHardware,
                                   server=server, adapter_nr=adapter_nr)
        adapter.delete()
    return HttpResponse()

def server_list_dvbadapters(request):
    "Returns avaible DVBWorld devices on server, excluding already used"
    pk = request.GET.get('server', None)
    server = get_object_or_404(models.Server, pk=pk)
    tuner_type = request.GET.get('type')
    if tuner_type == 'dvb':
        id_vendor = '04b4' # DVBWorld S/S2
    elif tuner_type == 'isdb':
        id_vendor = '1554' # PixelView SBTVD
    else:
        return HttpResponseBadRequest('Must specify the type of device')
    response = '<option value="">---------</option>'
    # Insert the currently selected
    tuner_pk = request.GET.get('tuner')
    if tuner_pk:
        tuner = get_object_or_404(models.DvbTuner, pk=tuner_pk)
        response += '<option value="%s">%s</option>' % (tuner.adapter,
                                        'DVBWorld %s' % tuner.adapter)
    # Populate the not used adapters left
    tuners = models.DvbTuner.objects.filter(server=server)
    adapters = models.DigitalTunerHardware.objects.filter(
        server=server, id_vendor='04b4') # DVBWorld S/S2
    for adapter in adapters:
        if not tuners.filter(adapter=adapter.uniqueid).exists():
            response += '<option value="%s">%s</option>' % (adapter.uniqueid,
                                            'DVBWorld %s' % adapter.uniqueid)
    
    return HttpResponse(response)

def server_available_isdbtuners(request):
    "Returns the number of non-used PixelView adapters"
    pk = request.GET.get('server', None)
    server = get_object_or_404(models.Server, pk=pk)
    # Insert the currently selected
    tuner_pk = request.GET.get('tuner')
    if tuner_pk:
        free_adapters = 1
    else:
        free_adapters = 0
    # Sum the free adapters left
    tuners = models.IsdbTuner.objects.filter(server=server).count()
    adapters = models.DigitalTunerHardware.objects.filter(
        server=server, id_vendor='1554').count()
    # Sanity check
    if tuners > adapters:
        raise Exception(
            'The total number of registered IsdbTuner objects '
            'is greater that the number of plugged-in PixelView adapters')
    
    return HttpResponse(free_adapters + (adapters - tuners))

def deviceserver_switch_link(request, method, klass, pk):
    device = get_object_or_404(klass, id=pk)
    try:
        if method == 'start':
            device.start()
        elif method == 'stop':
            device.stop()
        else:
            raise NotImplementedError()
    except Exception as ex:
        response = '%s: %s' % (ex.__class__.__name__, ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error' : response})
        return HttpResponseServerError(t.render(c))
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_%s_changelist' % klass._meta.module_name)
    return HttpResponseRedirect(url)

def dvbtuner_start(request, pk):
    tuner = get_object_or_404(models.DvbTuner, id=pk)
    try:
        tuner.start()
    except Exception as ex:
        response = '%s: %s' % (ex.__class__.__name__, ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error' : response})
        return HttpResponseServerError(t.render(c))
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_dvbtuner_changelist')
    return HttpResponseRedirect(url)

def dvbtuner_stop(request, pk):
    tuner = get_object_or_404(models.DvbTuner, id=pk)
    try:
        tuner.stop()
    except Exception as ex:
        response = '%s: %s' % (ex.__class__.__name__, ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error' : response})
        return HttpResponseServerError(t.render(c))
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_dvbtuner_changelist')
    return HttpResponseRedirect(url)

def isdbtuner_start(request, pk):
    tuner = get_object_or_404(models.IsdbTuner, id=pk)
    try:
        tuner.start()
    except Exception as ex:
        response = '%s: %s' % (ex.__class__.__name__, ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error' : response})
        return HttpResponseServerError(t.render(c))
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_isdbtuner_changelist')
    return HttpResponseRedirect(url)

def isdbtuner_stop(request, pk):
    tuner = get_object_or_404(models.IsdbTuner, id=pk)
    try:
        tuner.stop()
    except Exception as ex:
        response = '%s: %s' % (ex.__class__.__name__, ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error' : response})
        return HttpResponseServerError(t.render(c))
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_isdbtuner_changelist')
    return HttpResponseRedirect(url)

def unicastinput_start(request, pk):
    return deviceserver_switch_link(request, 'start',
        models.UnicastInput, pk)

def unicastinput_stop(request, pk):
    return deviceserver_switch_link(request, 'stop',
        models.UnicastInput, pk)

def multicastinput_start(request, pk):
    return deviceserver_switch_link(request, 'start',
        models.MulticastInput, pk)

def multicastinput_stop(request, pk):
    return deviceserver_switch_link(request, 'stop',
        models.MulticastInput, pk)

def file_start(request, pk=None):
    log = logging.getLogger('device.view')
    o = get_object_or_404(models.FileInput, id=pk)
    log.info('Starting %s', o)
    o.start()
    if o.status is True:
        log.info('File started with pid:%d', o.pid)
    else:
        log.warning('File could not start:%s', o)
    return HttpResponseRedirect(reverse('admin:device_vlc_changelist'))


def file_stop(request, pk=None):
    log = logging.getLogger('device.view')
    o = get_object_or_404(models.FileInput, id=pk)
    log.info('Stopping %s', o)
    o.stop()
    return HttpResponseRedirect(reverse('admin:device_vlc_changelist'))

def multicat_start(request,pk=None):
    print 'multicat_start'
    o = get_object_or_404(models.MulticatGeneric,id=pk)
    o.start()
    return HttpResponseRedirect(reverse('admin:device_multicatgeneric_changelist'))

def multicat_stop(request,pk=None):
    print 'multicat_stop'
    o = get_object_or_404(models.MulticatGeneric,id=pk)
    o.stop()
    return HttpResponseRedirect(reverse('admin:device_multicatgeneric_changelist'))

def multicat_redirect_start(request,pk=None):
    print 'multicat_redirect_start'
    o = get_object_or_404(models.MulticatRedirect,id=pk)
    o.start()
    return HttpResponseRedirect(reverse('admin:device_multicatredirect_changelist'))

def multicat_redirect_stop(request,pk=None):
    print 'multicat_redirect_stop'
    o = get_object_or_404(models.MulticatRedirect,id=pk)
    o.stop()
    return HttpResponseRedirect(reverse('admin:device_multicatredirect_changelist'))

def auto_fill_tuner_form(request, ttype):
    if request.method == 'GET':
        if ttype == 'dvbs':
            return render_to_response('dvbs_autofill_form.html',
                {'fields': forms.DvbTunerAutoFillForm},
                context_instance=RequestContext(request))
        elif ttype == 'isdb':
            return render_to_response('isdb_autofill_form.html',
                {'fields': forms.IsdbTunerAutoFillForm},
                context_instance=RequestContext(request))
    elif request.method == 'POST':
        if ttype == 'dvbs':
            return HttpResponse(\
'<script type="text/javascript">opener.dismissAutoFillPopup(window, "%s",\
"%s","%s", "%s", "%s");</script>' % \
(request.POST['freq'], request.POST['sr'], request.POST['pol'], \
 request.POST['mod'], request.POST['fec']))
        elif ttype == 'isdb':
            return HttpResponse(\
'<script type="text/javascript">opener.dismissAutoFillPopup(window, "%s");\
</script>' % \
(request.POST['freq']))


### Deixado como exemplo de como executar o play do TVoD (catchuptv)
#def tvod(request):
#    from player import Player
#    from django.conf import settings
#    import os
#    ip = request.META.get('REMOTE_ADDR')
#    seek = request.GET.get('seek')
#    channel_number = request.GET.get('channel')
#    channel = '%s/ch_%s' %(settings.CHANNEL_RECORD_DIR,channel_number)
#    action = request.GET.get('action')
#    # Grava:
#    # multicat -r 97200000000 -u @239.0.1.1:10000 /ldslsdld/dsasd/ch_3
#    # Roda unicast 5 min. 
#    # multicat -U -k -$((60*5*27000000)) /ldslsdld/dsasd/ch_3 192.168.0.244:5000
#    print('comando de tvod executado. seek: '+seek)
#    if seek:
#        seek = int(seek)
#    else:
#        seek =  60*5
#    port = 12000
#    if action == 'stop':
#        p = Player()
#        p.direct_stop(ip)
#        resposta = '{"status":"OK","command":"stop"}'
#        return HttpResponse(resposta,mimetype='application/javascript')
#    if os.path.exists(channel) is False:
#        resposta = '{"status":"ERROR","message":"channel record %s does not existis":"path":"%s"}' %(channel_number,channel)
#        return HttpResponse(resposta,mimetype='application/javascript')
#    p = Player()
#    pid = p.direct_play(channel, ip, port, seek)
#    resposta = '{"status":"OK","PID":"%s","seek":%s,"channel_path":"%s","destination":"%s"}' %(pid,seek,channel,'%s:%d'%(ip,port))
#    return HttpResponse(resposta,mimetype='application/javascript')
#    

