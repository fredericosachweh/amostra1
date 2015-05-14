# -*- encoding:utf8 -*
from __future__ import unicode_literals

import io
import logging
import re

from decimal import Decimal as D
from xlsxwriter import Workbook

from django.apps import apps
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views import generic
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

class Auth(View):
    mac_re = re.compile(r'^([0-9a-fA-F]{2}(:?|$)){6}$')

    def get(self, request):
        return HttpResponse('Invalid request, must be post', status=401)

    @method_decorator(csrf_exempt)
    def post(self, request):
        StreamPlayer = apps.get_model('device', 'StreamPlayer')
        SetTopBox = apps.get_model('client', 'SetTopBox')
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
        if SetTopBox.options.use_mac_as_serial is True and sn is None:
            sn = mac
        if SetTopBox.options.auto_create is True:
            stb, created = SetTopBox.objects.get_or_create(
                serial_number=sn,
                mac=mac)
            if created is True:
                log.debug('new stb autocreated:%s', stb)
        else:
            if SetTopBox.objects.filter(serial_number=sn).exists():
                stb = SetTopBox.objects.get(serial_number=sn)
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
            try:
                p.stop()
            except Exception as e:
                log.exception('Exception on stop:%s', e)
            p.delete()
        stb.online = False
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
    SetTopBox = apps.get_model('client', 'SetTopBox')
    log = logging.getLogger('client')
    mac = request.GET.get('mac') or request.GET.get('MAC')
    sn = request.GET.get('sn') or request.GET.get('SN')
    api_key = request.GET.get('api_key') or request.GET.get('api_key')
    nbridge = request.GET.get('nbridge') or request.GET.get('nbridge')
    ip = request.GET.get('ip') or request.GET.get('ip')
    log.debug(
        'User=%s, sn=%s, mac=%s, api_key=%s, nbridge=%s',
        request.user,
        sn,
        mac,
        api_key,
        nbridge
    )
    if SetTopBox.options.use_mac_as_serial is True and sn is None:
        sn = mac
    stb = SetTopBox.get_stb_from_user(request.user)
    if stb is not None:
        stb.online = True
        stb.nbridge_id = nbridge
        stb.ip = ip
        stb.save()
    return HttpResponse('OK', content_type='application/json')


@csrf_exempt
def offline(request):
    SetTopBox = apps.get_model('client', 'SetTopBox')
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
    if SetTopBox.options.use_mac_as_serial is True and sn is None:
        sn = mac
    stb = SetTopBox.get_stb_from_user(request.user)
    if stb is not None:
        stb.online = False
        stb.ip = None
        stb.nbridge_id = None
        stb.save()
    return HttpResponse('OK', content_type='application/json')


def change_route(request, stbs=None, key=None, cmd=None):
    import requests
    Nbridge = apps.get_model('nbridge', 'Nbridge')
    server_key = settings.NBRIDGE_SERVER_KEY
    log = logging.getLogger('client')
    log.debug('stbs=%s', stbs)
    log.debug('key=%s', key)
    log.debug('cmd=%s', cmd)
    stb_list = stbs.split(';')
    nbs = Nbridge.objects.filter(status=True)
    for s in nbs:
        url = 'http://%s:%s/route/%s' % (s.server.host, s.nbridge_port, cmd)
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
            return HttpResponse(
                'ERROR=%s' % (e), content_type='application/json'
            )
        finally:
            log.info('Finalizado o request')
    return HttpResponse('{"status": "OK"}', content_type='application/json')


def reload_channels(request, stbs=None, message=None):
    SetTopBox = apps.get_model('client', 'SetTopBox')
    log = logging.getLogger('api')
    if request.user.is_anonymous():
        return HttpResponse('Error: Unauthorized', status=401)
    macs = []
    stb_list = stbs.split(';')
    for m in stb_list:
        if len(m) == 17:
            macs.append(m)
    log.debug('Recebido=%s lista=%s', stbs, macs)
    stbs = SetTopBox.objects.filter(mac__in=macs)
    for s in stbs:
        log.debug('Enviando para o STB=%s, msg=%s', s, message)
        s.reload_channels(message=message)
    return HttpResponse('{"status": "OK"}', content_type='application/json')


def nbridge_down(request):
    SetTopBox = apps.get_model('client', 'SetTopBox')
    Nbridge = apps.get_models('nbridge', 'Nbridge')
    log = logging.getLogger('api')
    nbridge = request.GET.get('nbridge') or request.GET.get('nbridge')
    log.debug('Nbridge shutdown %s ', nbridge)
    nbobject = Nbridge.objects.get(pk=nbridge)
    SetTopBox.objects.filter(nbridge=nbobject).update(
        ip=None, online=False, nbridge=None
    )
    return HttpResponse('{"status": "OK"}', content_type='application/json')


def report_plans():
    SetTopBox = apps.get_model('client', 'SetTopBox')
    data = {}
    Plan = apps.get_model('client', 'Plan')
    plans = Plan.objects.all()
    stbs = SetTopBox.objects.all()
    stbs_total = stbs.count()
    stbs_principal = stbs.filter(
        Q(parent_set__isnull=False)|
        Q(parent__isnull=True)
    ).distinct()
    stbs_principal_total = stbs_principal.count()
    data['stbs_principal'] = {
        'total': stbs_principal_total,
        'percent': D(stbs_principal_total) / stbs_total * 100
    }
    stbs_secondary = stbs.filter(parent__isnull=False)
    stbs_secondary_total = stbs_secondary.count()
    data['stbs_secondary'] = {
        'total': stbs_secondary_total,
        'percent': D(stbs_secondary_total) / stbs_total * 100
    }
    data['plans'] = {}
    stbs_value = 0
    tvods_value = 0
    for plan in plans:
        subscriber_count = plan.subscriber_count()
        tvod_count = plan.tvod_count()
        data['plans'][plan] = {
            'stbs': subscriber_count,
            'stbs_value': subscriber_count * plan.value,
            'stbs_percent': D(subscriber_count) / stbs_principal_total * 100,
            'tvod': tvod_count,
            'tvod_value': tvod_count * plan.tvod_value,
        }
        stbs_value += subscriber_count * plan.value
        tvods_value += tvod_count * plan.tvod_value
    open_plan = stbs.filter(plan__isnull=True)
    stbs = open_plan.count()
    tvod = open_plan.filter(settopboxchannel__recorder=True).distinct().count()
    data['plans']['Outros'] = {
        'stbs': stbs,
        'tvod': tvod,
        'stbs_percent': D(stbs) / stbs_principal_total * 100,
    }
    data['stbs_total'] = stbs_total
    data['stbs_value'] = stbs_value
    data['tvods_value'] = tvods_value
    data['total_value'] = tvods_value + stbs_value
    return data


@login_required
def report_plans_xls(request):
    output = io.BytesIO()
    data = report_plans()
    wb = Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet()
    ws.write(0, 0, 'Quantidade de Assinantes')
    ws.write(0, 1, 'Quantidade de Assinantes Principais')
    ws.write(0, 2, '%')
    ws.write(0, 3, 'Quantidade de Assinantes Secundários')
    ws.write(0, 4, '%')
    ws.write(1, 0, data['stbs_total'])
    ws.write(1, 1, data['stbs_principal']['total'])
    ws.write(1, 2, data['stbs_principal']['percent'])
    ws.write(1, 3, data['stbs_secondary']['total'])
    ws.write(1, 4, data['stbs_secondary']['percent'])
    ws.write(2, 0, 'Dados de cobrança TV linear')
    ws.write(2, 3, 'Dados de cobrança TVoD')
    ws.write(3, 0, 'Planos')
    ws.write(3, 1, 'Quantidade de Assinantes')
    ws.write(3, 2, 'Total')
    ws.write(3, 3, '%')
    ws.write(3, 4, 'Planos')
    ws.write(3, 5, 'Quantidade de STBs com TVoD')
    ws.write(3, 6, 'Total')

    i = 4
    for plan, values in data['plans'].items():

        ws.write(i, 0, str(plan))
        ws.write(i, 1, values['stbs'])
        if 'stbs_value' in values:
            ws.write(i, 2, values['stbs_value'])
        ws.write(i, 3, values['stbs_percent'])
        ws.write(i, 4, str(plan))
        ws.write(i, 5, values['tvod'])
        if 'tvod_value' in values:
            ws.write(i, 6, values['tvod_value'])
        i += 1
    ws.write(i, 0, 'Total')
    i += 1
    ws.write(i, 0, 'Valor total TV linear')
    ws.write(i, 1, 'Valor total TVoD')
    ws.write(i, 2, 'Valor total')
    i += 1
    ws.write(i, 0, data['stbs_value'])
    ws.write(i, 1, data['tvods_value'])
    ws.write(i, 2, data['total_value'])
    wb.close()
    output.seek(0)
    response = HttpResponse(output.read())
    response['Content-Disposition'] = \
        'attachment; filename=relatorio_stbs.xlsx'
    return response


class SetTopBoxReportView(generic.ListView):
    SetTopBox = apps.get_model('client', 'SetTopBox')
    template_name = 'stbs_report.html'
    model = SetTopBox

    def get_context_data(self, **kwargs):
        context = super(SetTopBoxReportView, self).get_context_data(**kwargs)
        for key, value in report_plans().items():
            context[key] = value
        return context