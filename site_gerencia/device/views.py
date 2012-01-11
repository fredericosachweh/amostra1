
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import models

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def ssh_status(request,pk=None):
    print 'teste'
    device = get_object_or_404(models.Server,id=pk)
    device.statusUpdate()
    return HttpResponseRedirect(reverse('admin:device_server_changelist'))