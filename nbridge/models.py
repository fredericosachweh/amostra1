# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _
from device.models import DeviceServer
from django.template import Context, Template
from django.db import models
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings


class Nbridge(DeviceServer):
    middleware_addr = models.CharField('Middleware', max_length=100,
        blank=True, null=True, help_text=_('Ex. http://10.1.1.52/'))
    debug = models.BooleanField(_('Debug'), default=False)
    debug_port = models.PositiveSmallIntegerField(_('Porta'))

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

        link = '<a href="%s" id="id_%s" style="color:red;">Parado</a>' \
            % (url,self.id)

        if self.server.msg != 'OK':
            return '%s %s' % (self.server.msg, link)

        return link

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

        if self.debug and self.debug_port:
            cmd = '%s --debug=%s %s ' % (
                settings.NODEJS_COMMAND,
                self.debug_port,
                settings.NBRIDGE_COMMAND
            )

        if self.middleware_addr:
            cmd += '--middleware %s ' % self.middleware_addr

        cmd += '--bind %snbridge_%s.sock ' % (
            settings.NBRIDGE_SOCKETS_DIR, 
            self.id
        )

        try:
            log = "%snbridge_%s" % (settings.NBRIDGE_LOGS_DIR, self.id)
            self.pid = self.server.execute_daemon(cmd, log)
            self.status = True
            self.save()
        except:
            log = logging.getLogger('nbridge')
            log.error(self.server.msg)

        return self.server.msg

    def configure_nginx(self):
        servers = Nbridge.objects.filter(status=True)

        template = Template('''upstream nbridge {
                ip_hash;
                {% for s in servers %}
                server unix:{{socket_dir}}nbridge_{{s.id}}.sock;
                {% endfor %}
        }''')

        context = Context({
            'servers': servers, 
            'socket_dir': settings.NBRIDGE_SOCKETS_DIR
        })

        upstream = template.render(context)

        # Reset servers of nginx frontend upstream file.
        if servers.count() > 0:
            cmd = '/usr/bin/echo "%s" > %s' % (upstream, settings.NBRIDGE_UPSTREAM)
        else:
            cmd = '/bin/unlink %s' % (settings.NBRIDGE_UPSTREAM)
        self.server.execute(cmd)

        # Reload config of nginx frontend.
        self.server.execute('/usr/bin/sudo systemctl restart nginx-fe.service') 


@receiver(post_save, sender=Nbridge)
def nbridge_post_save(sender, instance, created, **kwargs):
    instance.configure_nginx()


