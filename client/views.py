# -*- encoding:utf8 -*
from __future__ import unicode_literals
import logging
import re
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from device.models import StreamPlayer
from django.conf import settings

from . import models
from nbridge.models import Nbridge

class Auth(View):
    mac_re = re.compile(r'^([0-9a-fA-F]{2}(:?|$)){6}$')

    def get(self, request):
        return HttpResponse('Invalid request, must be post', status=401)

    @method_decorator(csrf_exempt)
    def post(self, request):
        from tastypie.models import ApiKey
        log = logging.getLogger('client')
        mac = request.POST.get('mac') or request.POST.get('MAC')
        sn = request.POST.get('sn') or request.POST.get('SN')
        ip = request.POST.get('ip') or request.POST.get('IP')
        log.debug('auth:mac=%s, sn=%s, ip=%s', mac, sn, ip)
        if mac is None:
            return HttpResponse('Invalid request', status=401)
        valid = self.mac_re.match(mac)
        if valid is None:
            return HttpResponse('Invalid MAC', status=401)
        if models.SetTopBox.options.use_mac_as_serial is True and sn is None:
            sn = mac
        if models.SetTopBox.options.auto_create is True:
            stb, created = models.SetTopBox.objects.get_or_create(
                serial_number=sn,
                mac=mac)
            if created is True:
                log.debug('new stb autocreated:%s', stb)
        else:
            if models.SetTopBox.objects.filter(serial_number=sn).exists():
                stb = models.SetTopBox.objects.get(serial_number=sn)
            else:
                log.debug('SetTopBox don\'t existis:%s', sn)
                return HttpResponse('{"login": "ERROR"}', status=403)
        user = stb.get_user()
        a_user = authenticate(username=user.username, password=sn)
        if a_user is not None:
            login(request, a_user)
        else:
            log.debug('No user for SetTopBox:%s', stb)
            HttpResponse('{"login": "ERROR"}', status=403)
        log.debug('login: OK, user:%s', a_user)
        api_key = ApiKey.objects.get(user=a_user)
        log.debug('api_key:%s', api_key.key)
        players = StreamPlayer.objects.filter(stb=stb)
        for p in players:
            log.debug('Stop player %s', p)
            p.stop()
            p.delete()
        stb.online = True
        stb.ip = ip
        stb.save()
        response = HttpResponse(
            '{"login": "OK", "User": "%s", "api_key": "%s"}' % (
                a_user, api_key.key),
            content_type='application/json')
        response['Cache-Control'] = 'no-cache'
        return response


@csrf_exempt
def logoff(request):
    log = logging.getLogger('client')
    log.debug('logoff user:%s', request.user)
    logout(request)
    return HttpResponse('Bye', content_type='application/json')


@csrf_exempt
def online(request):
    log = logging.getLogger('client')
    mac = request.GET.get('mac') or request.GET.get('MAC')
    sn = request.GET.get('sn') or request.GET.get('SN')
    api_key = request.GET.get('api_key') or request.GET.get('api_key')
    nbridge = request.GET.get('nbridge') or request.GET.get('nbridge')
    log.debug(
        'User=%s, sn=%s, mac=%s, api_key=%s, nbridge=%s',
        request.user,
        sn,
        mac,
        api_key,
        nbridge
    )
    if models.SetTopBox.options.use_mac_as_serial is True and sn is None:
        sn = mac
    stb = models.SetTopBox.get_stb_from_user(request.user)
    if stb is not None:
        stb.online = True
        stb.nbridge_id = nbridge
        stb.save()
    return HttpResponse('OK', content_type='application/json')


@csrf_exempt
def offline(request):
    log = logging.getLogger('client')
    mac = request.GET.get('mac') or request.GET.get('MAC')
    sn = request.GET.get('sn') or request.GET.get('SN')
    api_key = request.GET.get('api_key') or request.GET.get('api_key')
    log.debug(
        'User=%s, sn=%s, mac=%s, api_key=%s',
        request.user,
        sn,
        mac,
        api_key
    )
    if models.SetTopBox.options.use_mac_as_serial is True and sn is None:
        sn = mac
    stb = models.SetTopBox.get_stb_from_user(request.user)
    if stb is not None:
        stb.online = False
        stb.ip = None
        stb.nbridge_id = None
        stb.save()
    return HttpResponse('OK', content_type='application/json')


def change_route(request, stbs=None, key=None, cmd=None):
    import requests
    server_key = settings.NBRIDGE_SERVER_KEY
    log = logging.getLogger('client')
    log.debug('stbs=%s', stbs)
    log.debug('key=%s', key)
    log.debug('cmd=%s', cmd)
    stb_list = stbs.split(';')
    nbs = Nbridge.objects.filter(status=True)
    for s in nbs:
        url = 'http://%s/ws/route/%s' % (s.server.host,cmd)
        macs = []
        # mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21
        for m in stb_list:
            macs.append(m)
        data = {
            'server_key': server_key,
            'mac[]': [macs]
            }
        log.debug('url=%s', url)
        log.debug('DATA=%s', data)
        try:
            response = requests.post(url, timeout=10, data=data)
            log.debug('Resposta=[%s]%s', response.status_code, response.text)
        except Exception as e:
            log.error('ERROR:%s', e)
            return HttpResponse('ERROR=%s' % (e), content_type='application/json')
        finally:
            log.info('Finalizado o request')    
    return HttpResponse('OK', content_type='application/json')
