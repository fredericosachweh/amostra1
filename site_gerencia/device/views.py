
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import models

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def server_status(request,pk=None):
    print 'server_status'
    device = get_object_or_404(models.Server,id=pk)
    whoami = device.execute('whoami')
    whoami = '' if device.execute('whoami') == None else whoami[0]
    device.status = (whoami.strip() == device.username.strip())
    device.save()
    return HttpResponseRedirect(reverse('admin:device_server_changelist'))

def vlc_start(request,pk=None):
    print 'vlc_start'
    vlc = get_object_or_404(models.Vlc,id=pk)
    vlc.start()
    return HttpResponseRedirect(reverse('admin:device_vlc_changelist'))

def vlc_stop(request,pk=None):
    print 'vlc_stop'
    vlc = get_object_or_404(models.Vlc,id=pk)
    vlc.stop()
    return HttpResponseRedirect(reverse('admin:device_vlc_changelist'))