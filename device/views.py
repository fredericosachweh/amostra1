# -*- encoding:utf-8 -*-
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.template import RequestContext, loader
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
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
        response += ('<option value="%s">%s</option>' % (i.pk, i))
    return HttpResponse(response)


@csrf_exempt
def server_update_adapter(request, pk, action):
    import re
    log = logging.getLogger('debug')
    adapter_nr = request.POST.get('adapter_nr')
    log.debug(u'Requisição para mudança de estado de um adapter')
    log.debug(u'server: %s, action: %s, adapter_nr: %s' % (
        pk, action, adapter_nr))
    server = get_object_or_404(models.Server, id=pk)
    # The adapter_nr will come in the format dvb1.frontend0, \
    # so I need to post process it
    aux = re.match(r'dvb(\d+)\.frontend\d+', adapter_nr)
    nr = aux.group(1)
    if action == 'add':
        try:
            adapter = models.DigitalTunerHardware.objects.get(server=server,
                                                        adapter_nr=nr)
            log.debug(u'adapter já existia na base de dados')
        except models.DigitalTunerHardware.DoesNotExist:
            adapter = models.DigitalTunerHardware(server=server,
                                                        adapter_nr=nr)
            log.debug(u'adapter vai ser inserido na base de dados')
        adapter.grab_info()
        adapter.save()
    elif action == 'remove':
        adapter = get_object_or_404(models.DigitalTunerHardware,
                                   server=server, adapter_nr=nr)
        adapter.delete()
        log.debug(u'o adapter %s foi removido da base de dados' % adapter)
    return HttpResponse()


def server_list_dvbadapters(request):
    "Returns avaible DVBWorld devices on server, excluding already used"
    pk = request.GET.get('server', None)
    server = get_object_or_404(models.Server, pk=pk)
    tuner_type = request.GET.get('type')
    if tuner_type == 'dvb':
        id_vendor = '04b4'  # DVBWorld S/S2
    elif tuner_type == 'isdb':
        id_vendor = '1554'  # PixelView SBTVD
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
        server=server, id_vendor='04b4')  # DVBWorld S/S2
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


def server_fileinput_scanfolder(request):
    pk = request.GET.get('server')
    server = get_object_or_404(models.Server, id=pk)
    l = u'<option value="">---------</option>\n'
    for f in server.list_dir(settings.VLC_VIDEOFILES_DIR):
        l += u'<option value="%s%s">%s</option>\n' % (
            settings.VLC_VIDEOFILES_DIR, f, f)
    return HttpResponse(l)


@csrf_exempt
def server_coldstart(request, pk):
    log = logging.getLogger('debug')
    log.debug('Iniciando rotina de coldstart no server com pk=%s' % pk)
    server = get_object_or_404(models.Server, id=pk)
    # Erase all
    models.DigitalTunerHardware.objects.filter(server=server).delete()
    # And create new ones
    tuners = server.auto_detect_digital_tuners()
    return HttpResponse(str(tuners))


def deviceserver_switchlink(request, action, klass, pk):
    device = get_object_or_404(klass, id=pk)
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_%s_changelist' % klass._meta.module_name)
    try:
        if action == 'start':
            device.start(recursive=True)
        elif action == 'stop':
            device.stop(recursive=True)
        elif action == 'recover':
            device.status = False
            if isinstance(device, models.IsdbTuner):
                device.adapter = None
            device.save()
        else:
            raise NotImplementedError()
    except Exception as ex:
        response = u'%s: %s' % (ex.__class__.__name__, ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error': response, 'return_url': url})
        return HttpResponseServerError(t.render(c))
    return HttpResponseRedirect(url)


def inputmodel_scan(request):
    "Scan's a input device showing the results to the user"
    ct = int(request.GET.get('ct'))
    ids = [int(i) for i in request.GET.get('ids').split(',')]
    model = ContentType.objects.get(pk=ct).model_class()
    queryset = model.objects.filter(pk__in=ids)
    opts = model._meta
    if len(queryset) == 1:
        objects_name = force_unicode(model._meta.verbose_name)
    else:
        objects_name = force_unicode(model._meta.verbose_name_plural)
    try:
        results = [(device, device.scan()) for device in queryset]
    except models.InputModel.GotNoLockException as ex:
        response = _(u'Sem sinal: "%s"' % ex)
        t = loader.get_template('device_500.html')
        c = RequestContext(request, {'error': response})
        return HttpResponseServerError(t.render(c))
    context = {
        'results': results,
        'objects_name': objects_name,
        'app_label': model._meta.app_label,
        'opts': opts,
    }
    return TemplateResponse(request, 'scan_result.html', context)


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


def multicat_start(request, pk=None):
    print 'multicat_start'
    o = get_object_or_404(models.MulticastInput, id=pk)
    o.start()
    return HttpResponseRedirect(reverse(
        'admin:device_multicatgeneric_changelist'))


def multicat_stop(request, pk=None):
    print 'multicat_stop'
    o = get_object_or_404(models.MulticastInput, id=pk)
    o.stop()
    return HttpResponseRedirect(reverse(
        'admin:device_multicatgeneric_changelist'))


def multicat_redirect_start(request, pk=None):
    print 'multicat_redirect_start'
    o = get_object_or_404(models.MulticastInput, id=pk)
    o.start()
    return HttpResponseRedirect(reverse(
        'admin:device_multicatredirect_changelist'))


def multicat_redirect_stop(request, pk=None):
    print 'multicat_redirect_stop'
    o = get_object_or_404(models.MulticastInput, id=pk)
    o.stop()
    return HttpResponseRedirect(reverse(
        'admin:device_multicatredirect_changelist'))


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


def tvod(request, channel_number=None, command=None, seek=0):
    u'TVOD commands'
    from datetime import timedelta
    from django.utils import timezone
    from models import StreamPlayer, StreamRecorder
    from tv.models import Channel
    from django.core.cache import get_cache
    cache = get_cache('default')
    log = logging.getLogger('device.view')
    resp = 'Not running'
    ## Get IP addr form STB
    ip = request.META.get('REMOTE_ADDR')
    ## Find request on cache
    key = 'tvod_ip_%s' % ip
    state = cache.get(key)
    if state is None:
        cache.set(key, 1)
    else:
        log.debug('duplicated request key:%s', key)
        return HttpResponse(u'DUP REC', mimetype='application/javascript')
    log.info('tvod[%s] client:%s channel:%s seek:%s' % (command, ip,
        channel_number, seek))
    ## Load channel
    channel = get_object_or_404(Channel, number=channel_number)
    ## Verifica se existe gravação solicitada
    record_time = timezone.now() - timedelta(0, int(seek))
    ## Find a recorder with request
    log.info('rec.filter: start_time__lte=%s, channel=%s, keep_time__gte=%d',
        record_time, channel, (int(seek) / 3600))
    recorders = StreamRecorder.objects.filter(start_time__lte=record_time,
        channel=channel, keep_time__gte=(int(seek) / 3600))
    log.info('avaliable recorders: %s' % recorders)
    if len(recorders) == 0:
        log.info('Record Unavaliable')
        cache.delete(key)
        return HttpResponse(u'Unavaliable', mimetype='application/javascript')
    ## Verifica se existe um player para o cliente
    if StreamPlayer.objects.filter(stb_ip=ip).count() == 0:
        StreamPlayer.objects.create(
            stb_ip=ip,
            server=recorders[0].server,
            recorder=recorders[0]
            )
        log.info('new player created to ip: %s' % ip)
    player = StreamPlayer.objects.get(stb_ip=ip)
    player.recorder = recorders[0]
    player.server = recorders[0].server
    player.save()
    if command == 'play':
        try:
            player.play(time_shift=int(seek))
        except Exception as e:
            log.error(e)
            resp = 'Error'
        if player.pid and player.status:
            resp = 'OK'
        else:
            log.error('Can not start: status=%s pid=%s' % (player.status,
                player.pid))
            resp = 'Can not start'
    elif command == 'stop':
        if player.pid and player.status:
            player.stop()
        resp = 'Stoped'
    log.debug('Player: %s', player)
    cache.delete(key)
    return HttpResponse(resp, mimetype='application/javascript')


def tvod_list(request):
    u'Get list of current recorders'
    import simplejson
    from datetime import timedelta
    from django.utils import timezone
    import time
    from models import StreamRecorder
    log = logging.getLogger('device.view')
    ip = request.META.get('REMOTE_ADDR')
    log.debug('tvod_list from ip=%s' % ip)
    rec = StreamRecorder.objects.filter(status=True)
    meta = {
        'previous': "",
        'total_count': 0,
        'offset': 0,
        'limit': 0,
        'next': ""
    }
    obj = []
    for r in rec:
        meta['total_count'] += 1
        rec_time = timezone.now() - timedelta(hours=int(r.keep_time))
        if r.start_time < rec_time:
            start = rec_time
        else:
            start = r.start_time
        obj.append({
            'id': r.id,
            'start': time.mktime(start.timetuple()),
            'start_as_string': str(start),
            'record_time': int(r.keep_time) * 3600,
            'channel': r.channel.number
            })
    json = simplejson.dumps({'meta': meta, 'objects': obj})
    if request.GET.get('format') == 'jsonp' and \
        request.GET.get('callback') == None:
        json = 'callback(' + json + ')'
    if request.GET.get('callback') != None:
        json = request.GET.get('callback') + '(' + json + ')'
    return HttpResponse(json, mimetype='application/javascript')
