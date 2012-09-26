# -*- encoding:utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from device.models import FileInput, MulticastInput, UnicastInput, IsdbTuner
from device.models import DvbTuner
from django.core.urlresolvers import reverse
from device.models import UniqueIP, DemuxedService

import models
import logging


def channel_switchlink(request, action, pk):
    channel = get_object_or_404(models.Channel, id=pk)
    if action == 'start':
        channel.start()
    elif action == 'stop':
        channel.stop()
    url = request.META.get('HTTP_REFERER')
    if url is None:
        url = reverse('admin:tv_channel_changelist')
    return HttpResponseRedirect(url)


def input_list_interfaces(request):
    log = logging.getLogger('tv.view')
    pk = request.GET.get('type')
    log.debug('Type com pk=%s', pk)
    table = {'arquivos_de_entrada': FileInput.objects.all(),
             'entradas_multicast': MulticastInput.objects.all(),
             'entradas_unicast': UnicastInput.objects.all(),
             'isdb': IsdbTuner.objects.all(),
             'dvbs': DvbTuner.objects.all()}[pk]
    response = '<option selected="selected" value="">---------</option>'
    for v in table:
        response += ('<option value="%s">%s %s</option>' % (v.id,
v.description, v))
    return HttpResponse(response)


def get_content_type_id(content_type_key):
    ''' Values from device_content_type '''
    content_type = {'dvbs': 26,
                    'isdb': 27,
                    'entradas_unicast': 28,
                    'entradas_multicast': 29}[content_type_key]
    return content_type


def get_demux_input_list(request):
    input_type = request.GET.get('type')
    if input_type == 'arquivos_de_entrada':
        f_text = '<option selected="selected" value="-1">Não usado</option>'
        return HttpResponse(f_text)
    content_type_id = get_content_type_id(input_type)
    objects_ids = []
    for ip in UniqueIP.objects.all():
        objects_ids.append(ip.object_id)
    model = DemuxedService.objects.all()
    for ob_id in objects_ids:
        model = model.exclude(deviceserver_ptr_id=ob_id)
    model = model.exclude(content_type_id=content_type_id)
    response = '<option selected="selected" value="">---------</option>'
    for m in model:
        response += ('<option value="%s">%s</option>' % (m.id, m))
    return HttpResponse(response)
