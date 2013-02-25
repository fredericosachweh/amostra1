# -*- encoding:utf8 -*

import logging
from django.http import HttpResponse
from django.contrib.auth import login, authenticate

import models


def auth(request, mac=None):
    u"""Realiza a autenticação do setupbox atravéz de seu endereço MAC"""
    log = logging.getLogger('client')
    log.debug('auth:%s', mac)
    if models.SetTopBox.options.autocreate is True:
        stb, created = models.SetTopBox.objects.get_or_create(
            serial_number=mac)
        if created is True:
            log.debug('new stb autocreated:%s', stb)
    else:
        if models.SetTopBox.objects.filter(serial_number=mac).exists() is True:
            stb = models.SetTopBox.objects.get(serial_number=mac)
        else:
            log.debug('SetTopBox don\'t existis:%s', mac)
            return HttpResponse(status=401)
    user = stb.get_user()
    a_user = authenticate(username=user.username, password=mac)
    if a_user is not None:
        login(request, a_user)
    else:
        log.debug('No user for SetTopBox:%s', stb)
        HttpResponse(status=401)
    log.debug('login: OK, user:%s', a_user)
    return HttpResponse('{"login": "OK", "User": "%s"}' % (a_user))

