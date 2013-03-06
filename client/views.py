# -*- encoding:utf8 -*

import logging
import re
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import models


class Auth(View):
    mac_re = re.compile(r'^([0-9a-fA-F]{2}(:?|$)){6}$')

    def get(self, request):
        return HttpResponse('Invalid request, must post', status=401)

    @method_decorator(csrf_exempt)
    def post(self, request):
        log = logging.getLogger('client')
        mac = request.POST.get('mac')
        sn = request.POST.get('sn')
        log.debug('auth:mac=%s, sn=%s', mac, sn)
        if mac is None:
            return HttpResponse('Invalid request', status=401)
        valid = self.mac_re.match(mac)
        if valid is None:
            return HttpResponse(u'Invalid MAC', status=401)
        if models.SetTopBox.options.use_mac_as_serial is True and sn is None:
            sn = mac
        if models.SetTopBox.options.auto_create is True:
            stb, created = models.SetTopBox.objects.get_or_create(
                serial_number=sn,
                mac=mac)
            if created is True:
                log.debug('new stb autocreated:%s', stb)
        else:
            if models.SetTopBox.objects.filter(serial_number=mac).exists():
                stb = models.SetTopBox.objects.get(serial_number=sn)
            else:
                log.debug('SetTopBox don\'t existis:%s', mac)
                return HttpResponse(u'{"login": "ERROR"}', status=403)
        user = stb.get_user()
        a_user = authenticate(username=user.username, password=sn)
        if a_user is not None:
            login(request, a_user)
        else:
            log.debug('No user for SetTopBox:%s', stb)
            HttpResponse(u'{"login": "ERROR"}', status=403)
        log.debug('login: OK, user:%s', a_user)
        response = HttpResponse('{"login": "OK", "User": "%s"}' % (a_user),
            content_type='application/json')
        response['Cache-Control'] = 'no-cache'
        return response


@csrf_exempt
def logoff(request):
    log = logging.getLogger('client')
    log.debug('logoff user:%s', request.user)
    logout(request)
    return HttpResponse('Bye', content_type='application/json')
