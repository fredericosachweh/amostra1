# -*- encoding:utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from device.models import FileInput, MulticastInput, UnicastInput, IsdbTuner
from device.models import DvbTuner
from django.core.urlresolvers import reverse

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
        response += ('<option value="%s">%s %s</option>' % (v, v.description,
v))
    return HttpResponse(response)
