# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
import models

def monserver_status(request, pk=None):
    server = get_object_or_404(models.MonServer, id=pk)
    server.connect()
    #log = logging.getLogger('.view')
    #log.debug('server_status(pk=%s)', pk)
    #if server.status is True:
    #    log.error(u'Cant connect with server:(%s) %s:%d %s',
    #        server, server.host, server.ssh_port, server.msg)
    #else:
    #    server.auto_create_nic()
    #log.info('Server:%s [%s]', server, server.status)
    #log.info('server_status(pk=%s)', pk)
    return HttpResponseRedirect(reverse('admin:monitoramento_monserver_changelist'))

