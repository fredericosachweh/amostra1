# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import logging
from tempfile import NamedTemporaryFile

from django.utils.translation import ugettext as _
from device.models import DeviceServer
from django.template import Context, Template
from django.db import models
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db.models import signals
from django.conf import settings
log = logging.getLogger('nbridge')

CHOICES_ENV_VAR = (
    ('production', 'Ambiente de Produção', ),
    ('development', 'Ambiente de Desenvolvimento', )
)

class Nbridge(DeviceServer):
    middleware_addr = models.CharField('Middleware', max_length=100,
        blank=True, null=True, help_text=_('Ex. http://10.1.1.52/'))
    debug = models.BooleanField(_('Debug'), default=False)
    debug_port = models.PositiveSmallIntegerField(_('Porta'))
    log_level = models.PositiveSmallIntegerField('Nível de log', default=0,
        help_text=_('Nível de log para debug interno (0, 1, 2 ou 3)'))
    env_val = models.CharField('Ambiente de execução', default='production',
        max_length=20, help_text=_('Tipo de execução'), choices=CHOICES_ENV_VAR
        )

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
            % (url, self.id)

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

    def _status_and_pid(self):
        is_running = False
        pid = 0
        if self.status == False:
            return False, 0
        pidcommand = '/usr/bin/sudo systemctl status nbridge@%s.service'\
            % (self.id)
        output = self.server.execute(pidcommand, check=False)
        for l in output:
            ar = l.split()
            if ar.count('Active:') and ar.count('(running)'):
                is_running = True
            if ar.count('PID:') == 1:
                pid = ar[2]
        return is_running, pid

    def running(self):
        status, pid = self._status_and_pid()
        log.info('Nbridge[%i] Status=%s pid=%s', self.id, status, pid)
        return status

    def start(self, *args, **kwargs):
        try:
            systemd_cmd = '/usr/bin/sudo systemctl start nbridge@%s.service'\
                % (self.id)
            self.server.execute(systemd_cmd)
            status, pid = self._status_and_pid()
            self.pid = pid
            self.status = True
            self.save()
        except Exception as e:
            log.error('ERRO:%s', e)
            log.error(self.server.msg)

        return self.server.msg

    def stop(self, *args, **kwargs):
        systemd_cmd = '/usr/bin/sudo systemctl stop nbridge@%s.service'\
            % (self.id)
        self.server.execute(systemd_cmd)
        self.pid = None
        self.status = False
        self.save()

    def configure_nginx(self):
        servers = Nbridge.objects.filter(status=True, server=self.server)

        template = Template('''upstream nbridge {
    ip_hash;{% for s in servers %}
    server unix:{{socket_dir}}nbridge_{{s.id}}.sock;{% endfor %}}''')

        context = Context({
            'servers': servers, 
            'socket_dir': settings.NBRIDGE_SOCKETS_DIR
        })

        upstream = template.render(context)

        # Reset servers of nginx frontend upstream file.
        if servers.count() > 0:
            cmd = '/usr/bin/echo "%s" > %s' % (upstream, settings.NBRIDGE_UPSTREAM)
        else:
            upstream = '''upstream nbridge {
    ip_hash;
    server unix:%snbridge_fake.sock;
}''' % (settings.NBRIDGE_SOCKETS_DIR)
            cmd = '/usr/bin/echo "%s" > %s' % (upstream, settings.NBRIDGE_UPSTREAM)
        self.server.execute(cmd)

        # Reload config of nginx frontend.
        self.server.execute('/usr/bin/sudo systemctl restart nginx-fe.service')

    def configure_systemd(self):
        servers = Nbridge.objects.filter(server=self.server)
        sysconfig = ''
        for s in servers:
            if s.debug and s.debug_port > 0:
                sysconfig += 'NODEARGS_%s="--debug=%d"\n' % (s.id, s.debug_port)
            else:
                sysconfig += 'NODEARGS_%s=""\n' % (s.id)
        log.debug('sysconfig=%s', sysconfig)
        ## Create and copy
        remote_tmpfile = self.server.create_tempfile()
        tmpfile = NamedTemporaryFile()
        tmpfile.file.write(sysconfig)
        tmpfile.file.flush()
        self.server.put(tmpfile.name, remote_tmpfile)
        cmd_sysconfig = '/usr/bin/sudo /usr/bin/cp %s /etc/sysconfig/nbridge' % (remote_tmpfile)
        log.debug('Config sysconfig=%s', cmd_sysconfig)
        self.server.execute(cmd_sysconfig)
        self.server.rm_file(remote_tmpfile)
        
    def create_config(self):
        config_file = "%sconfig_%i.json" % (settings.NBRIDGE_CONF_DIR, self.id)
        if self.log_level > 0:
            verbose = 'true'
        else:
            verbose = 'false'
        config = '''{
    "bind": "%snbridge_%s.sock",
    "middleware": "%s",
    "api": "/tv/api",
    "server_key": "%s",
    "verbose": %s,
    "log_level": %s,
    "env": "%s",
    "nbridge_id": "%s"
}''' % (settings.NBRIDGE_SOCKETS_DIR, self.id,
            self.middleware_addr,
            settings.NBRIDGE_SERVER_KEY or '36410c96-c157-4b2a-ac19-1a2b7365ca11',
            verbose,
            self.log_level,
            self.env_val,
            self.id)
        cmd = '/usr/bin/echo \'%s\' > %s' % (config, config_file)
        self.server.execute(cmd)



@receiver(signals.post_save, sender=Nbridge)
def nbridge_post_save(sender, instance, created, **kwargs):
    instance.configure_nginx()
    instance.configure_systemd()
    instance.create_config()


