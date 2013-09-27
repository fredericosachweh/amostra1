# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import models


def status_switchlink(request, action, pk):
    nbridge = get_object_or_404(models.Nbridge, id=pk)

    url = reverse('admin:nbridge_nbridge_changelist')

    if action == 'start':
        nbridge.start(recursive=True)
    elif action == 'stop':
        nbridge.stop(recursive=True)
    else:
        raise NotImplementedError()

    return HttpResponseRedirect(url)
