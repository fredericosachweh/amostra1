# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
import thread
import logging

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
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.decorators import login_required
from . import models
from . import forms
# Para requer admin:
# @user_passes_test(lambda u: u.is_superuser)


def home(request):
    return HttpResponseRedirect(reverse('admin:index'))


@login_required
def server_status(request, pk=None):
    server = get_object_or_404(models.Server, id=pk)
    server.connect()
    log = logging.getLogger('device.view')
    log.debug('server_status(pk=%s)', pk)
    if server.status is False:
        log.error(
            'Cant connect with server:(%s) %s:%d %s',
            server, server.host, server.ssh_port, server.msg
        )
    else:
        server.auto_create_nic()
    log.info('Server:%s [%s]', server, server.status)
    log.info('server_status(pk=%s)', pk)
    return HttpResponseRedirect(reverse('admin:device_server_changelist'))


@login_required
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


@login_required
def server_list_storages(request):
    log = logging.getLogger('device.view')
    pk = request.GET.get('server')
    log.debug('Server com pk=%s', pk)
    server = get_object_or_404(models.Server, id=pk)
    log.info('Listing Storage from server (pk=%s)', pk)
    response = '<option selected="selected" value="">---------</option>'
    for i in models.Storage.objects.filter(server=server):
        response += ('<option value="%s">%s</option>' % (i.pk, i))
    return HttpResponse(response)


@csrf_exempt
@login_required
def server_update_adapter(request, pk, action):
    import re
    log = logging.getLogger('debug')
    adapter_nr = request.POST.get('adapter_nr')
    log.debug('Requisição para mudança de estado de um adapter')
    log.debug('server: %s, action: %s, adapter_nr: %s' % (
        pk, action, adapter_nr))
    server = get_object_or_404(models.Server, id=pk)
    # The adapter_nr will come in the format dvb1.frontend0, \
    # so I need to post process it
    aux = re.match(r'dvb(\d+)\.frontend\d+', adapter_nr)
    if aux is None:
        return HttpResponse('invalid format\r\n', status=401)
    nr = aux.group(1)
    if action == 'add':
        try:
            adapter = models.DigitalTunerHardware.objects.get(
                server=server, adapter_nr=nr
            )
            log.debug('adapter já existia na base de dados')
        except models.DigitalTunerHardware.DoesNotExist:
            adapter = models.DigitalTunerHardware(
                server=server, adapter_nr=nr
            )
            log.debug('adapter vai ser inserido na base de dados')
        adapter.grab_info()
        adapter.save()
    elif action == 'remove':
        adapter = get_object_or_404(
            models.DigitalTunerHardware, server=server, adapter_nr=nr
        )
        adapter.delete()
        log.debug('o adapter %s foi removido da base de dados' % adapter)
    return HttpResponse('')


@login_required
def server_list_dvbadapters(request):
    "Returns avaible DVBWorld devices on server, excluding already used"
    log = logging.getLogger('debug')
    pk = request.GET.get('server', None)
    server = get_object_or_404(models.Server, pk=pk)
    tuner_type = request.GET.get('type')
    log.info('List device type:%s on server:%s', tuner_type, server)
    if tuner_type == 'dvb':
        # id_vendor = '04b4'  # DVBWorld S/S2
        pass
    elif tuner_type == 'isdb':
        # id_vendor = '1554'  # PixelView SBTVD
        pass
    else:
        return HttpResponseBadRequest('Must specify the type of device')
    response = '<option value="">---------</option>'
    # Insert the currently selected
    tuner_pk = request.GET.get('tuner')
    if tuner_pk:
        # tuner = get_object_or_404(models.DvbTuner, pk=tuner_pk)
        # response += '<option value="%s">%s</option>' % (tuner.adapter,
        #     tuner.adapter)
        tuners = models.DvbTuner.objects.filter(server=server).exclude(
            pk=tuner_pk)
    else:
        # Populate the not used adapters left
        tuners = models.DvbTuner.objects.filter(server=server)
    adapters = models.DigitalTunerHardware.objects.filter(
        server=server, id_vendor__in=['04b4', '1131'])  # DVBWorld S/S2
    for adapter in adapters:
        if not tuners.filter(adapter=adapter.uniqueid).exists():
            response += '<option value="%s">%s (%s - %s:%s)</option>' % (
                adapter.uniqueid, adapter.uniqueid, adapter.bus,
                adapter.id_vendor, adapter.id_product)
    return HttpResponse(response)


@login_required
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


@login_required
def server_fileinput_scanfolder(request):
    pk = request.GET.get('server')
    server = get_object_or_404(models.Server, id=pk)
    l = '<option value="">---------</option>\n'
    for f in server.list_dir(settings.VLC_VIDEOFILES_DIR):
        l += '<option value="%s%s">%s</option>\n' % (
            settings.VLC_VIDEOFILES_DIR, f, f)
    return HttpResponse(l)


@csrf_exempt
@login_required
def server_coldstart(request, pk):
    log = logging.getLogger('debug')
    log.debug('Iniciando rotina de coldstart no server com pk=%s', pk)
    server = get_object_or_404(models.Server, id=pk)
    # Erase all
    models.DigitalTunerHardware.objects.filter(server=server).delete()
    # And create new ones
    tuners = server.auto_detect_digital_tuners()
    return HttpResponse(str(tuners))


@login_required
def deviceserver_switchlink(request, action, klass, pk):
    device = get_object_or_404(klass, id=pk)
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:device_%s_changelist' % (klass._meta.module_name))
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
    return HttpResponseRedirect(url)


@login_required
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
        response = _('Sem sinal: "%s"' % ex)
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


@login_required
def auto_fill_tuner_form(request, ttype):
    if request.method == 'GET':
        if ttype == 'dvbs':
            return render_to_response(
                'dvbs_autofill_form.html',
                {'fields': forms.DvbTunerAutoFillForm},
                context_instance=RequestContext(request)
            )
        elif ttype == 'isdb':
            return render_to_response(
                'isdb_autofill_form.html',
                {'fields': forms.IsdbTunerAutoFillForm},
                context_instance=RequestContext(request)
            )
    elif request.method == 'POST':
        if ttype == 'dvbs':
            return HttpResponse(
                '<script type="text/javascript">opener.dismissAutoFillPopup('
                'window, "%s", "%s","%s", "%s", "%s");</script>' % (
                    request.POST['freq'],
                    request.POST['sr'],
                    request.POST['pol'],
                    request.POST['mod'],
                    request.POST['fec']
                )
            )
        elif ttype == 'isdb':
            return HttpResponse(
                '<script type="text/javascript">opener.dismissAutoFillPopup('
                'window, "%s");</script>' % (request.POST['freq'])
            )


def run_play(player, seektime, cache, key):
    player.play(time_shift=int(seektime))
    cache.delete(key)


def get_random_on_storage(recorders):
    from random import randint
    log = logging.getLogger('tvod')
    soma = 0
    s = 0
    for r in recorders:
        soma += r.storage.peso
    rand = randint(0, soma)
    log.debug('Soma=%d, Rand=%d', soma, rand)
    for r in recorders:
        s += r.storage.peso
        if s >= rand:
            return r


def tvod(request, channel_number=None, command=None, seek=0):
    'TVOD commands'
    from datetime import timedelta
    from django.utils import timezone
    from models import StreamPlayer, StreamRecorder
    from tv.models import Channel
    from client.models import SetTopBox, SetTopBoxChannel
    from django.core.cache import get_cache
    import hashlib
    # TODO: Limit number of players
    # from django.db.models import F
    # q = StreamRecorder.objects.filter(
    #     storage__n_players__lt=F('storage__limit_play_hd') + 1)
    cache = get_cache('default')
    log = logging.getLogger('tvod')
    status = cache._cache.get_stats()
    if len(status) == 0:
        log.error('Memcached is not running')
        return HttpResponse(
            '{"status": "error" ,"error": "memcached not running"}',
            content_type='application/javascript',
            status=500
        )
    resp = ''
    # Get IP addr form STB
    ip = request.META.get('REMOTE_ADDR')
    # Get ticket from querystring
    ticket = request.GET.get('ticket', None)
    stop_ticket_key = 'tvod_stop_ticket_%s' % (ip)
    # Get path to create stop hash
    md5_path = hashlib.md5(request.path).hexdigest()
    stop_key = 'tvod_stop_key_%s' % (md5_path)
    # Find request on cache
    key = 'tvod_ip_%s' % ip
    key_value = cache.get(key)
    if key_value is None:
        log.info('cache new key="%s"', key)
        if command != 'stop':
            cache.set(key, 1, 4)  # Define o lock com timeout de 4 segundos
    else:
        log.error('duplicated request key:"%s", cmd=%s', key, command)
        if command != 'stop':
            return HttpResponse(
                '{"status": "error" ,"error": "duplicated request"}',
                content_type='application/javascript',
                status=409
            )
    if key_value == 1:
        log.error('player is starting key:%s', key_value)
        if command != 'stop':
            return HttpResponse(
                '{"status": "error" ,"error": "Another instance is starting"}',
                content_type='application/javascript',
                status=409
            )
    log.info(
        'tvod[%s] client:"%s" channel:"%s" seek:"%s"',
        command, ip, channel_number, seek
    )
    # User
    if request.user.is_anonymous():
        log.debug('User="%s" can\'t play', request.user)
        cache.delete(key)
        return HttpResponse(
            '{"status": "error" ,"error": "Anonymous request"}',
            content_type='application/javascript',
            status=401
        )
    if request.user.groups.filter(name='settopbox').exists():
        serial = request.user.username.replace(settings.STB_USER_PREFIX, '')
        stb = SetTopBox.objects.get(serial_number=serial)
        log.info('Filter for STB=%s', stb)
    else:
        cache.delete(key)
        log.warn('Not a STB (not on settopbox group)')
        return HttpResponse(
            '{"status": "error" ,"error": "Not a STB"}',
            content_type='application/javascript',
            status=401
        )
    # Colocando o stop antes de outros comandos
    if command == 'stop':
        stop_ticket = cache.get(stop_ticket_key)
        if stop_ticket != ticket and ticket is not None:
            return HttpResponse(
                '{"status": "error" ,"error": "Stop ignored - invalid ticket"}',
                content_type='application/javascript',
                status=412
            )
        can_stop = cache.get('tvod_stop_key_%s' % (seek))
        if can_stop is None and key_value is not None:
            return HttpResponse(
                '{"status": "error" ,"error": "Stop ignored"}',
                content_type='application/javascript',
                status=409
            )
        try:
            player = StreamPlayer.objects.get(stb_ip=ip)
        except:
            log.error('cmd=%s but no player with ip=%s', command, ip)
            return HttpResponse(
                '{"status": "error" ,"error": "Player not fould"}',
                content_type='application/javascript',
                status=401
            )
        if player.pid and player.status:
            player.stop()
        resp = command
        cache.delete(key)
        cache.delete(can_stop)
        return HttpResponse(
            '{"status":"%s", "port":%d}' % (resp, player.stb_port),
            content_type='application/javascript',
            status=200
        )
    # Load channel
    try:
        channel = Channel.objects.get(number=channel_number)
    except:
        cache.delete(key)
        log.warning('Channel not found: %s', request.get_full_path())
        return HttpResponse(
            '{"status": "error" ,"error": "Channel not found"}',
            content_type='application/javascript',
            status=404
        )
    # Verifica se o STB tem acesso à gravações para o canal
    stb_ch = SetTopBoxChannel.objects.filter(
        settopbox=stb, channel=channel
    ).first()
    if stb_ch is None:
        cache.delete(key)
        log.warning('No access on channel')
        return HttpResponse(
            '{"status": "error" ,"error": "No access on channel"}',
            content_type='application/javascript',
            status=401
        )
    elif stb_ch.recorder is False:
        cache.delete(key)
        log.warning('No access on recorder')
        return HttpResponse(
            '{"status": "error" ,"error": "No access on recorder"}',
            content_type='application/javascript',
            status=401
        )

    seek = int(seek)

    record_time = timezone.now() - timedelta(seconds=seek)
    log.debug(
        'Agora(%s) - delta(%s) = %s',
        timezone.now(),
        timedelta(seconds=seek),
        record_time
    )

    # Find a recorder with request
    log.debug(
        'rec.filter: start_time__lte=%s, channel=%s, keep_time__gte=%d',
        record_time, channel, (seek / 3600)
    )
    recorders = StreamRecorder.objects.filter(
        status=True,
        channel__settopboxchannel__settopbox=stb,
        channel__settopboxchannel__recorder=True,
        start_time__lte=record_time,
        channel=channel,
        keep_time__gte=(int(seek / 3600))
    )
    log.info('avaliable recorders: %s', recorders)
    if recorders.count() == 0:
        log.info('Record Unavaliable')
        cache.delete(key)
        return HttpResponse(
            '{"status": "error" ,"error": "Record not found"}',
            content_type='application/javascript',
            status=404
        )
    # Priorize server (random)
    recorder = get_random_on_storage(recorders)
    log.debug('Current recorder:%s', recorder)
    # Verifica se existe um player para o cliente
    if StreamPlayer.objects.filter(stb_ip=ip).count() == 0:
        StreamPlayer.objects.create(
            stb_ip=ip,
            server=recorder.server,
            recorder=recorder,
            stb=stb
        )
        log.debug('new player created to ip: %s', ip)
    player = StreamPlayer.objects.get(stb_ip=ip)
    log.debug(
        'Current channel=%s, New channel=%s',
        channel,
        player.recorder.channel
    )
    if player.status and player.pid and channel == player.recorder.channel:
        pass
    else:
        if player.server != recorder.server:
            player.stop()
        player.recorder = recorder
        player.server = recorder.server
        player.stb_port = settings.CHANNEL_PLAY_PORT
        player.save()
    cache.set(stop_key, 1, 4)
    # Define a chave de ticket
    cache.set(stop_ticket_key, ticket, 43200)  # Timeout de 12 horas
    if command == 'play':
        try:
            if player.status and player.pid:
                player.stb_port += 1
            thread.start_new_thread(run_play, (player, seek, cache, key))
            resp = ''
            return HttpResponse(
                '{"response":"%s", "port":%d}' % (resp, player.stb_port),
                content_type='application/javascript',
                status=200
            )
            # player.play(time_shift=int(seek))
        except Exception as e:
            log.error(e)
            resp = ''
    elif command == 'pause':
        resp = player.pause(time_shift=int(seek))
        resp = ''
    log.debug('Player: %s', player)
    cache.delete(key)
    return HttpResponse(
        '{"status":"%s", "port":%d}' % (resp, player.stb_port),
        content_type='application/javascript',
        status=200
    )


def tvod_list(request):
    'Get list of current recorders'
    import simplejson
    from datetime import timedelta
    from django.utils import timezone
    import time
    from models import StreamRecorder
    from client.models import SetTopBox
    log = logging.getLogger('tvod')
    meta = {
        'previous': "",
        'total_count': 0,
        'offset': 0,
        'limit': 0,
        'next': ""
    }
    obj = []
    if request.user.is_anonymous():
        log.debug('Return empt list to %s', request.user)
        json = simplejson.dumps({'meta': meta, 'objects': obj})
        return HttpResponse(json, content_type='application/javascript')
    if request.user.groups.filter(name='settopbox').exists():
        serial = request.user.username.replace(settings.STB_USER_PREFIX, '')
        stb = SetTopBox.objects.get(serial_number=serial)
        log.debug('Filter for STB=%s', stb)
    else:
        json = simplejson.dumps({'meta': meta, 'objects': obj})
        return HttpResponse(json, content_type='application/javascript')
    ip = request.META.get('REMOTE_ADDR')
    log.debug('tvod_list from ip=%s' % ip)
    rec = StreamRecorder.objects.filter(
        status=True,
        channel__settopboxchannel__settopbox=stb,
        channel__settopboxchannel__recorder=True
    )
    log.debug('Recorders:%s', rec)
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
    if request.GET.get('format') == 'jsonp'\
            and request.GET.get('callback') is None:
        json = 'callback(' + json + ')'
    if request.GET.get('callback') is not None:
        json = request.GET.get('callback') + '(' + json + ')'
    return HttpResponse(json, content_type='application/javascript')
