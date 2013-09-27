# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from device.models import DeviceServer
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


class Nbridge(DeviceServer):
    middleware_addr = models.CharField('Middleware', max_length=100,
        blank=True, null=True, help_text=_('Ex. http://10.1.1.25/'))

    def switch_link(self):
        module_name = self._meta.module_name
        running = self.running()

        if running == False and self.status == True:
            url = reverse('%s_recover' % module_name,
                kwargs={'pk': self.id})

            return 'Crashed<a href="%s" id="%s_id_%s" style="color:red;">' \
                   ' ( Recuperar )</a> ' % (
                    url, module_name, self.id)

        if running == True and self.status == True:
            url = reverse('%s_stop' % module_name,
                kwargs={'pk': self.id})

            return '<a href="%s" id="%s_id_%s" style="color:green;">' \
                   'Rodando</a>' % (url, module_name, self.id)

        url = reverse('%s_start' % module_name,
            kwargs={'pk': self.id})

        return '<a href="%s" id="%s_id_%s" style="color:red;">Parado</a>' \
            % (url, module_name, self.id)

    switch_link.allow_tags = True
    switch_link.short_description = u'Status'

    def __unicode__(self):
        return '%s' % self.server.name

    class Meta:
        ordering = ['server__name']
        verbose_name = _('Servidor NBridge')
        verbose_name_plural = _('Servidores NBridge')

    def start(self, *args, **kwargs):
        cmd = '%s %s ' % (settings.NODEJS_COMMAND, settings.NBRIDGE_COMMAND)

        if (self.middleware_addr):
            cmd += '--middleware %s ' % self.middleware_addr

        self.pid = self.server.execute_daemon(cmd, settings.NBRIDGE_LOGS_DIR)
        self.status = True
        self.save()

