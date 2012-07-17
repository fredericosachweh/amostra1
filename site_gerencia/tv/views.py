# -*- encoding:utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

import models


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
