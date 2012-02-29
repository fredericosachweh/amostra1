
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import models

def home(request):
    return HttpResponse('Na raiz do sistema <a href="%s">Admin</a>'%reverse('admin:index'))

def server_status(request,pk=None):
    device = get_object_or_404(models.Server,id=pk)
    device.connect()
    whoami = device.execute('whoami')
    whoami = '' if device.execute('whoami') == None else whoami[0]
    device.status = (whoami.strip() == device.username.strip())
    device.save()
    print('Device:%s [%s]' %(device,device.status))
    print 'server_status'
    return HttpResponseRedirect(reverse('admin:device_server_changelist'))

def vlc_start(request,pk=None):
    print 'vlc_start'
    o = get_object_or_404(models.Vlc,id=pk)
    o.start()
    return HttpResponseRedirect(reverse('admin:device_vlc_changelist'))

def vlc_stop(request,pk=None):
    print 'vlc_stop'
    o = get_object_or_404(models.Vlc,id=pk)
    o.stop()
    return HttpResponseRedirect(reverse('admin:device_vlc_changelist'))

def multicat_start(request,pk=None):
    print 'multicat_start'
    o = get_object_or_404(models.Multicat,id=pk)
    o.start()
    return HttpResponseRedirect(reverse('admin:device_multicat_changelist'))

def multicat_stop(request,pk=None):
    print 'multicat_stop'
    o = get_object_or_404(models.Multicat,id=pk)
    o.stop()
    return HttpResponseRedirect(reverse('admin:device_multicat_changelist'))
