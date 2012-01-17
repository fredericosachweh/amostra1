
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import models

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def ssh_status(request,pk=None):
    print 'whoami'
    device = get_object_or_404(models.Server,id=pk)
    device.execute('whoami')
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