# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from device.models import DeviceServer
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


class Nbridge(DeviceServer):
    middleware_addr = models.CharField('Middleware', max_length=100,
        blank=True, null=True, help_text=_('Ex. http://10.1.1.52/'))

    def switch_link(self):
        running = self.running()

        if running == False and self.status == True:
            url = reverse('nbridge.views.status_switchlink',
                kwargs={'action': 'recover', 'pk': self.id})

            return 'Crashed<a href="%s" id="id_%s" style="color:red;">' \
                   ' ( Recuperar )</a> ' % (url, self.id)

        if running == True and self.status == True:
            url = reverse('nbridge.views.status_switchlink',
                kwargs={'action': 'stop', 'pk': self.id})

            return '<a href="%s" id="id_%s" style="color:green;">' \
                   'Rodando</a>' % (url, self.id)

        url = reverse('nbridge.views.status_switchlink',
            kwargs={'action':'start', 'pk': self.id})

        return '<a href="%s" id="id_%s" style="color:red;">Parado</a>' \
            % (url,self.id)

    switch_link.allow_tags = True
    switch_link.short_description = u'Status'

    def __unicode__(self):
        return '%s' % self.server.name

    class Meta:
        ordering = ['server__name']
        verbose_name = _('Servidor NBridge')
        verbose_name_plural = _('Servidores NBridge')

    def start(self, *args, **kwargs):
        import pdb; pdb.set_trace()

        cmd = '%s %s ' % (settings.NODEJS_COMMAND, settings.NBRIDGE_COMMAND)

        if (self.middleware_addr):
            cmd += '--middleware %s ' % self.middleware_addr

        cmd += '--bind %s%s.sock' % (settings.NBRIDGE_SOCKETS_DIR, self.id)

        self.pid = self.server.execute_daemon(cmd, settings.NBRIDGE_LOGS_DIR)
        self.status = True
        self.save()

