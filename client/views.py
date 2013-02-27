# -*- encoding:utf8 -*

import logging
import re
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt

import models
mac_re = re.compile(r'^([0-9a-fA-F]{2}(:?|$)){6}$')

@csrf_exempt
def auth(request):
    u"""Realiza a autenticação do setupbox atravéz de seu endereço MAC,SN"""
    log = logging.getLogger('client')
    mac = request.POST.get('MAC')
    sn = request.POST.get('SN')
    valid = mac_re.match(mac)
    if valid is None:
        return HttpResponse(u'Invalid MAC', status=401)
    if models.SetTopBox.options.use_mac_as_serial is True and sn is None:
        sn = mac
    log.debug('auth:mac=%s, sn=%s', mac, sn)
    if models.SetTopBox.options.auto_create is True:
        stb, created = models.SetTopBox.objects.get_or_create(
            serial_number=sn,
            mac=mac)
        if created is True:
            log.debug('new stb autocreated:%s', stb)
    else:
        if models.SetTopBox.objects.filter(serial_number=mac).exists() is True:
            stb = models.SetTopBox.objects.get(serial_number=sn)
        else:
            log.debug('SetTopBox don\'t existis:%s', mac)
            return HttpResponse(status=403)
    user = stb.get_user()
    a_user = authenticate(username=user.username, password=sn)
    if a_user is not None:
        login(request, a_user)
    else:
        log.debug('No user for SetTopBox:%s', stb)
        HttpResponse(status=403)
    log.debug('login: OK, user:%s', a_user)
    return HttpResponse('{"login": "OK", "User": "%s"}' % (a_user), content_type='application/json')


def logoff(request):
    log = logging.getLogger('client')
    log.debug('logoff user:%s', request.user)
    logout(request)
    return HttpResponse('Bye', content_type='application/json')
