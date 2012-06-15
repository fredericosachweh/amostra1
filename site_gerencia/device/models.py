#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from __future__ import division
import logging
from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Server(models.Model):
    """
    Servidor e caracteristicas de conexão.
    """

    name = models.CharField(_(u'Nome'), max_length=200, unique=True)
    host = models.IPAddressField(_(u'Host'), blank=True, unique=True)
    username = models.CharField(_(u'Usuário'), max_length=200, blank=True)
    password = models.CharField(_(u'Senha'), max_length=200, blank=True)
    rsakey = models.CharField(_(u'Chave RSA'),
        help_text='Exemplo: ~/.ssh/id_rsa',
        max_length=500,
        blank=True)
    ssh_port = models.PositiveSmallIntegerField(_(u'Porta SSH'),
        blank=True, null=True, default=22)
    modified = models.DateTimeField(_(u'Última modificação'), auto_now=True)
    status = models.BooleanField(_(u'Status'), default=False)
    msg = models.TextField(_(u'Mensagem de retorno'), blank=True)
    SERVER_TYPE_CHOICES = (
                         (u'local', _(u'Servidor local DEMO')),
                         (u'dvb', _(u'Sintonizador DVB')),
                         (u'recording', _(u'Servidor TVoD')),
                         )
    server_type = models.CharField(_(u'Tipo de Servidor'), max_length=100,
                                   choices=SERVER_TYPE_CHOICES)
    offline_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = _(u'Servidor de Recursos')
        verbose_name_plural = _(u'Servidores de Recursos')

    class ExecutionFailure(Exception):
        pass

    class InvalidOperation(Exception):
        pass

    def __unicode__(self):
        return '%s' % (self.name)

    def switch_link(self):
        url = reverse('device.views.server_status', kwargs={'pk': self.id})
        return '<a href="%s" id="server_id_%s" >Atualizar</a>' % (url, self.id)

    switch_link.allow_tags = True
    switch_link.short_description = u'Status'

    def clean(self):
        from django.core.exceptions import ValidationError
        if str(self.server_type) == 'local' and str(self.host) != '127.0.0.1':
            raise ValidationError(_(
                u'Servidor DEMO só pode ser usado com IP local 127.0.0.1.'
                ))

    @property
    def is_local(self):
        return True if str(self.server_type) == 'local' else False

    def connect(self):
        """Conecta-se ao servidor"""
        from lib import ssh
        if self.offline_mode:
            raise Server.InvalidOperation(
                "Shouldn't connect when offline mode is set")
        s = None
        try:
            s = ssh.Connection(host=self.host,
                port=self.ssh_port,
                username=self.username,
                password=self.password,
                private_key=self.rsakey)
            self.status = True
            self.msg = 'OK'
        except Exception as ex:
            log = logging.getLogger('device.remotecall')
            log.error('%s(%s:%s %s):%s' % (self, self.host, self.ssh_port,
                self.username, ex))
            self.status = False
            self.msg = ex
        self.save()
        return s

    def execute(self, command, persist=False):
        """Executa um comando no servidor"""
        try:
            s = self.connect()
            self.msg = 'OK'
        except Exception as ex:
            self.msg = 'Can not connect:' + str(ex)
            log = logging.getLogger('device.remotecall')
            log.error('[%s]:%s' % (self, ex))
            self.save()
            return 'Can not connect'
        ret = s.execute(command)
        if not persist and self.status:
            s.close()
        self.save()
        if ret.get('exit_code') and ret['exit_code'] is not 0:
                raise Server.ExecutionFailure(
                    u'Command "%s" returned status "%d" on server "%s": "%s"' %
                    (command, ret['exit_code'], self, u"".join(ret['output'])))
        return ret['output']

    def execute_daemon(self, command, log_path=None):
        "Excuta o processo em background (daemon)"
        try:
            s = self.connect()
            self.msg = 'OK'
        except Exception as ex:
            self.msg = ex
            self.status = False
            log = logging.getLogger('device.remotecall')
            log.error('[%s]:%s' % (self, ex))
            raise ex
        ret = s.execute_daemon(command, log_path)
        exit_code = ret.get('exit_code')
        if exit_code is not 0:
            raise Server.ExecutionFailure(
                    u'Command "%s" returned status "%d" on server "%s": "%s"' %
                    (command, ret['exit_code'], self, u"".join(ret['output'])))
        pid = ret['pid']
        s.close()
        self.save()
        return int(pid)

    def get(self, remotepath, localpath=None):
        """Copies a file between the remote host and the local host."""
        s = self.connect()
        s.get(remotepath, localpath)
        s.close()

    def put(self, localpath, remotepath=None):
        """Copies a file between the local host and the remote host."""
        s = self.connect()
        s.put(localpath, remotepath)
        s.close()

    def process_alive(self, pid):
        "Verifica se o processo está em execução no servidor"
        log = logging.getLogger('debug')
        for p in self.list_process():
            if p['pid'] == pid:
                log.info('Process [%d] live on [%s] = True', pid, self)
                return True
        log.info('Process [%d] live on [%s] = False', pid, self)
        return False

    def list_process(self):
        """
        Retorna a lista de processos rodando no servidor
        """
        ps = '/bin/ps -eo pid,comm,args'
        stdout = self.execute(ps)
        ret = []
        for line in stdout[1:]:
            cmd = line.split()
            ret.append({
                'pid': int(cmd[0]),
                'name': cmd[1],
                'command': ' '.join(cmd[2:])
                })
        return ret

    def kill_process(self, pid):
        u"Mata um processo em execução"
        if type(pid) is not int:
            raise Exception('kill_process expect a number as argument')
        s = self.connect()
        resp = s.execute('/bin/kill %d' % pid)
        s.close()
        return resp

    def auto_detect_digital_tuners(self):
        import re
        resp = []
        try:
            devices = self.list_dir('/dev/dvb/')
        except Server.ExecutionFailure:
            # This can happen if the /dev/dvb folder doesn't exist
            # or the ssh user doesn't has access permission
            return None
        for device in devices:
            adapter = DigitalTunerHardware(server=self)
            match = re.match(r'^adapter(\d+)$', device)
            # Sometimes the adapter folder exits
            # but the frontend0 file is not there
            if match and \
                'frontend0' in self.list_dir('/dev/dvb/%s' % device):
                adapter.adapter_nr = match.groups()[0]
                adapter.grab_info()
                adapter.save()
                resp.append(adapter)
        return resp

    def auto_create_nic(self):
        """
        Auto create NIC (Network interfaces)
        """
        log = logging.getLogger('debug')
        log.info('Auto create NIC on %s', self)
        nics = []
        for iface in self._list_interfaces():
            nnics = NIC.objects.filter(name=iface['dev'], server=self).count()
            if nnics == 0:
                nic = NIC.objects.create(name=iface['dev'], server=self,
                    ipv4=iface['ip'])
                log.info('    New NIC found %s', nic)
            else:
                nic = NIC.objects.get(name=iface['dev'], server=self)
                nic.ipv4 = iface['ip']
                log.info('    Existing NIC %s', nic)
            nic.ipv4 = iface['ip']
            nics.append(nic)
        return nics

    def _list_interfaces(self):
        "List server's configured network interfaces"
        import re
        result = self.execute('/sbin/ip -f inet addr show')
        response = []
        for r in result:
            match = re.findall(r'((\d{1,3}\.){3}\d{1,3}).* (.*)$', r.strip())
            if match:
                response.append({'ip': match[0][0], 'dev': match[0][2]})
        return response

    def get_netdev(self, ip):
        "Retorna o NIC que tem este ip neste servidor"
        return NIC.objects.get(server=self, ipv4=ip).name

    def create_route(self, ip, dev):
        "Create a new route on the server"
        log = logging.getLogger('debug')
        log.info('Creating route on %s dev= %s to %s', self, dev, ip)
        routes = self.list_routes()
        # Skip if the route already exists
        try:
            routes.index((ip, dev))
        except ValueError:
            self.execute('/usr/bin/sudo /sbin/route add -host %s dev %s'
                % (ip, dev))

    def delete_route(self, ip, dev):
        "Delete a route on the server"
        log = logging.getLogger('debug')
        log.info('Deleting route on %s dev= %s to %s', self, dev, ip)
        routes = self.list_routes()
        # Skip if the route don't exist
        try:
            routes.index((ip, dev))
            self.execute('/usr/bin/sudo /sbin/route del -host %s dev %s'
                % (ip, dev))
        except Exception as e:
            log.error('Error deleting route on %s [%s %s]:%s', self, dev, ip,
                e)

    def list_routes(self):
        log = logging.getLogger('debug')
        log.info('Listing routes on %s', self)
        resp = []
        routes = self.execute('/sbin/route -n')
        for route in routes[2:]:
            r = route.split()
            resp.append((r[0], r[-1]))
        return resp

    def list_dir(self, directory='/'):
        "Lista o diretório no servidor retornando uma lista do conteúdo"
        log = logging.getLogger('debug')
        log.info('Listing dir on server "%s" dir="%s"', self, directory)
        ret = self.execute('/bin/ls %s' % directory)
        return map(lambda x: x.strip('\n'), ret)

    def cat_file(self, path):
        "Return the contents of a File given his path"
        ret = self.execute('/bin/cat %s' % path)
        content = u''.join(ret)
        return content.strip()

    def file_exists(self, path):
        try:
            self.execute('/bin/ls %s' % path)
        except Server.ExecutionFailure:
            return False
        return True

    def rm_file(self, path):
        self.execute('/bin/rm -f %s' % path)

    def create_tempfile(self):
        "Creates a temp file and return it's path"
        return "".join(self.execute('/bin/mktemp')).strip()


@receiver(post_save, sender=Server)
def Server_post_save(sender, instance, created, **kwargs):
    "Signal to prepare the server for use"
    from tempfile import NamedTemporaryFile
    from helper.template_scripts import INIT_SCRIPT, UDEV_CONF, MODPROBE_CONF
    if created is True and instance.offline_mode is False:
        if instance.connect() is None:
            log = logging.getLogger('debug')
            log.info("The server %s was unreachable, " \
                     "so we couldn't configure it", instance)
            return  # There is nothing we can do
        instance.auto_create_nic()
        instance.auto_detect_digital_tuners()
        # Create the tmpfiles
        remote_tmpfile = instance.create_tempfile()
        # Create the udev rules file
        cmd = "/usr/bin/env |" \
              "/bin/grep SSH_CLIENT |" \
              "/bin/grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'"
        my_ip = "".join(instance.execute(cmd)).strip()
        udev_conf = UDEV_CONF % \
            {'my_ip': my_ip, 'my_port': settings.MIDDLEWARE_WEBSERVICE_PORT,
             'add_url': reverse('server_adapter_add', args=[instance.pk]),
             'rm_url': reverse('server_adapter_remove', args=[instance.pk])}
        tmpfile = NamedTemporaryFile()
        tmpfile.file.write(udev_conf)
        tmpfile.file.flush()
        instance.put(tmpfile.name, remote_tmpfile)
        instance.execute('/usr/bin/sudo /bin/cp -f %s ' \
                         '/etc/udev/rules.d/87-iptv.rules' % remote_tmpfile)
        # Create the init script to report a server boot event
        init_script = INIT_SCRIPT % \
            {'my_ip': my_ip, 'my_port': settings.MIDDLEWARE_WEBSERVICE_PORT,
             'status_url': reverse('device.views.server_status',
                kwargs={'pk': instance.pk}),
             'coldstart_url': reverse('device.views.server_coldstart',
                kwargs={'pk': instance.pk})}
        tmpfile = NamedTemporaryFile()
        tmpfile.file.write(init_script)
        tmpfile.file.flush()
        instance.put(tmpfile.name, remote_tmpfile)
        instance.execute('/usr/bin/sudo /bin/cp -f %s ' \
                         '/etc/init.d/iptv_coldstart' % remote_tmpfile)
        instance.execute('/usr/bin/sudo /bin/chmod +x ' \
                         '/etc/init.d/iptv_coldstart')
        instance.execute('/usr/bin/sudo /sbin/chkconfig iptv_coldstart on')
        # Create the modprobe config file
        tmpfile = NamedTemporaryFile()
        tmpfile.file.write(MODPROBE_CONF)
        tmpfile.file.flush()
        instance.put(tmpfile.name, remote_tmpfile)
        instance.execute('/usr/bin/sudo /bin/cp -f %s ' \
                         '/etc/modprobe.d/iptv-cianet.conf' % remote_tmpfile)


class NIC(models.Model):
    'Classe de manipulação da interface de rede e referencia do servidor'
    name = models.CharField(_(u'Interface de rede'), max_length=50)
    server = models.ForeignKey(Server)
    ipv4 = models.IPAddressField(_(u'Endereço ip v4 atual'))

    class Meta:
        unique_together = ('name', 'server')

    def __unicode__(self):
        return u'%s->%s(%s)' % (self.server, self.name, self.ipv4)


class UniqueIP(models.Model):
    """
    Classe de endereço ip externo (na rede dos clientes)
    """
    class Meta:
        verbose_name = _(u'Endereço IPv4 multicast')
        verbose_name_plural = _(u'Endereços IPv4 multicast')
    ip = models.IPAddressField(_(u'Endereço IP'),
        unique=True,
        null=True)
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    #nic = models.ForeignKey(NIC)
    sequential = models.PositiveSmallIntegerField(
        _(u'Valor auxiliar para gerar o IP único'),
        default=2)

    ## Para o relacionamento genérico de origem
    sink = generic.GenericForeignKey()
    content_type = models.ForeignKey(ContentType,
        limit_choices_to={"model__in": ("DemuxedService", "FileInput")},
        blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        if self.sink is None:
            sink = u''
            sink_classname = u''
        else:
            sink = self.sink
            sink_classname = self.sink.__class__.__name__
        src_connections = [unicode(con) for con in self.src]
        ret = u'%s %s --> [ %s:%d ] <-- { %s }' % (
            sink_classname, sink, self.ip,
            self.port, ", ".join(src_connections),
        )
        return ret

    def sink_str(self):
        if self.sink is None:
            return u''
        return u'<a href="%s">&lt;%s&gt; %s</a>' % (
            reverse('admin:device_%s_change' % self.sink._meta.module_name,
                args=[self.sink.pk]), self.sink._meta.verbose_name, self.sink)
    sink_str.allow_tags = True
    sink_str.short_description = _(u'Entrada (sink)')

    def src_str(self):
        if len(self.src) is 0:
            return u''
        ret = []
        for obj in self.src:
            ret.append(u'<a href="%s">&lt;%s&gt; %s</a>' % (
                reverse('admin:device_%s_change' % obj._meta.module_name,
                    args=[obj.pk]), obj._meta.verbose_name, obj))
        return u"<br />".join(ret)
    src_str.allow_tags = True
    src_str.short_description = _(u'Saídas (src)')

    @property
    def src(self):
        from itertools import chain
        uniqueip_type = ContentType.objects.get_for_model(UniqueIP)
        ipout = MulticastOutput.objects.filter(content_type=uniqueip_type,
                                               object_id=self.pk)
        recorder = StreamRecorder.objects.filter(content_type=uniqueip_type,
                                               object_id=self.pk)
        return list(chain(ipout, recorder))

    def natural_key(self):
        return {'ip': self.ip, 'port': self.port}

    def save(self, *args, **kwargs):
        if UniqueIP.objects.count() > 0:
            anterior = UniqueIP.objects.latest('sequential')
            proximo = anterior.sequential + 1
            mod = proximo % 256
            if mod == 255:
                proximo += 3
            if mod == 0:
                proximo += 2
            if mod == 1:
                proximo += 1
            self.sequential = proximo
        if self.ip is None:
            self.ip = self._gen_ip()
        super(UniqueIP, self).save(*args, **kwargs)

    def _gen_ip(self):
        ip = settings.EXTERNAL_IP_MASK % (
            self.sequential / 256,
            self.sequential % 256)
        return ip

    @classmethod
    def create(klass, sink=None):
        obj = klass()
        obj.ip = obj._gen_ip()
        obj.sink = sink
        obj.save()
        return obj

    def start(self, *args, **kwargs):
        self.sink.start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        self.sink.stop(*args, **kwargs)


class DeviceServer(models.Model):
    """
    Aplicativo que roda em um determinado servidor.
    O metodo start deve ser sobreescrito com o comando específico
    """
    server = models.ForeignKey(Server, verbose_name=_(u'Servidor de recursos'))
    status = models.BooleanField(_(u'Status'), default=False, editable=False)
    pid = models.PositiveSmallIntegerField(_(u'PID'),
        blank=True, null=True, editable=False)
    description = models.CharField(_(u'Descrição'), max_length=250, blank=True)

    class AlreadyRunning(Exception):
        pass

    class NotRunning(Exception):
        pass

    def _type(self):
        return _(u'undefined')

    def start(self):
        log = logging.getLogger('debug')
        log.info('Iniciando device %s', self)

    def stop(self):
        """Interrompe processo no servidor"""
        log = logging.getLogger('debug')
        log.info('Parando device %s', self)
        try:
            self.server.kill_process(self.pid)
            self.status = False
            self.pid = None
        except ValueError:
            print('Execute error: %s' % ValueError)
        self.save()
        return not self.status

    def server_status(self):
        return self.server.status
    server_status.boolean = True

    def link_status(self):
        if self.status and self.server.status:
            return True
        return False
    link_status.boolean = True

    def running(self):
        if self.status is True:
            alive = self.server.process_alive(self.pid)
        else:
            alive = False
        return alive

    def switch_link(self):
        module_name = self._meta.module_name
        if (hasattr(self, 'src') and self.src is None) or \
           (hasattr(self, 'sink') and self.sink is None):
            return _(u'Desconfigurado')
        running = self.running()
        if running is False and self.status is True:
            url = reverse('%s_recover' % module_name,
                kwargs={'pk': self.id})
            return 'Crashed<a href="%s" id="%s_id_%s" style="color:red;">' \
                   ' ( Recuperar )</a>' % (url, module_name, self.id)
        if running is True and self.status is True:
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


class Dvblast(DeviceServer):
    "DEPRECATED: Não utilizado mais???"
    class Meta:
        verbose_name = _(u'DVBlast')
        verbose_name_plural = _(u'DVBlast')

    name = models.CharField(_(u'Nome'), max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    is_rtp = models.BooleanField(_(u'RTP'), default=False)

    def __unicode__(self):
        return '%s (%s:%s)' % (self.name, self.ip, self.port)

    def status(self):
        from lib.player import Player
        p = Player()
        if p.is_playing(self) is True:
            url = reverse('device.views.stop', kwargs={'streamid': self.id})
            return '<a href="%s" id="stream_id_%s" style="color:green;" >\
Rodando</a>' % (url, self.id)
        url = reverse('device.views.play', kwargs={'streamid': self.id})
        return '<a href="%s" id="stream_id_%s" style="color:red;" >Parado</a>'\
            % (url, self.id)
    status.allow_tags = True

    def play(self):
        'Inicia o fluxo (inicia o processo do multicat)'
        from lib.player import Player
        p = Player()
        pid = p.play_stream(self)
        self.pid = pid
        self.save()


class Antenna(models.Model):
    class Meta:
        verbose_name = _(u'Antena parabólica')
        verbose_name_plural = _(u'Antenas parabólicas')

    LNBS = (
            (u'normal_c', u'C Normal'),
            (u'multiponto_c', u'C Multiponto'),
            (u'universal_ku', u'Ku Universal'),
            )

    satellite = models.CharField(_(u'Satélite'), max_length=200)
    lnb_type = models.CharField(_(u'Tipo de LNB'), max_length=200,
        choices=LNBS, help_text=_(u'Verificar o tipo de LNBf escrito ' \
                                  u'no cabeçote da antena'))

    def __unicode__(self):
        return str(self.satellite)


class DemuxedService(DeviceServer):
    class Meta:
        verbose_name = _(u'Entrada demultiplexada')
        verbose_name_plural = _(u'Entradas demultiplexadas')

    sid = models.PositiveIntegerField(_(u'Programa'))
    provider = models.CharField(_(u'Provedor'), max_length=2000, null=True,
        blank=True)
    service_desc = models.CharField(_(u'Serviço'), max_length=2000, null=True,
        blank=True)
    enabled = models.BooleanField(default=False)
    src = generic.GenericRelation(UniqueIP)
    nic_src = models.ForeignKey(NIC, blank=True, null=True)
    # Sink (connect to a Tuner or IP input)
    content_type = models.ForeignKey(ContentType,
        limit_choices_to={"model__in":
            ("DvbTuner", "IsdbTuner", "UnicastInput", "MulticastInput")},
         null=True)
    object_id = models.PositiveIntegerField(null=True)
    sink = generic.GenericForeignKey()

    def __unicode__(self):
        return ('[%d] %s - %s') % (self.sid, self.provider, self.service_desc)

    def start(self, *args, **kwargs):
        self.enabled = True
        self.status = True
        self.save()
        if self.sink.status is True:
            self.sink.reload_config()
        else:
            self.sink.start()

    def stop(self, *args, **kwargs):
        self.enabled = False
        self.status = False
        self.save()
        if self.sink.running() is True:
            if kwargs.get('recursive') is True:
                self.sink.reload_config(shutdown_gracefully=True)
            else:
                self.sink.reload_config()

    def running(self):
        return self.enabled and self.status and self.sink.running()

    def switch_link(self):
        if self.src.count() is 0:
            return _(u'Desconfigurado')
        return super(DemuxedService, self).switch_link()
    switch_link.allow_tags = True
    switch_link.short_description = u'Status'


class InputModel(models.Model):
    "Each model of input type should inherit this"
    class Meta:
        abstract = True

    class GotNoLockException(Exception):
        "Could not lock signal"
        pass

    def _list_enabled_services(self):
        return self.src.filter(enabled=True)

    def _list_all_services(self):
        return self.src.all()

    def start_all_services(self):
        for service in self._list_all_services():
            service.start()

    def _get_config(self):
        # Fill config file
        conf = u''
        for service in self._list_enabled_services():
            if service.src.count() > 0:
                sid = service.sid
                ip = service.src.all()[0].ip
                port = service.src.all()[0].port
                nic = service.nic_src
                conf += u'%s:%d' % (ip, port)
                if nic is not None:
                    conf += u'@%s' % nic.ipv4
                # Assume internal IPs always work under raw UDP
                conf += u'/udp 1 %d\n' % sid

        return conf

    def reload_config(self, shutdown_gracefully=False):
        from lxml import etree
        conf = self._get_config()
        # Write the config file to disk
        self.server.execute('echo "%s" > %s%d.conf' % (conf,
                        settings.DVBLAST_CONFS_DIR, self.pk))
        try:
            self._read_ctl('reload')
        except etree.XMLSyntaxError:
            # This is expected: the reload command returns an empty string
            pass
        if len(conf) is 0 and shutdown_gracefully is True:
            self.stop()

    def stop(self):
        for service in self._list_enabled_services():
            service.stop()
        super(InputModel, self).stop()
        # Clean socket file
        path = u'%s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        if self.server.file_exists(path):
            self.server.rm_file(path)

    def _create_folders(self):
        "Creates all the folders dvblast needs"

        def create_folder(path):
            try:
                self.server.execute('/usr/bin/sudo /bin/mkdir -p %s' % path)
                self.server.execute('/usr/bin/sudo /bin/chown %s:%s %s' % (
                    self.server.username, self.server.username, path))
            except Exception as ex:
                log = logging.getLogger('debug')
                log.error(unicode(ex))

        create_folder(settings.DVBLAST_CONFS_DIR)
        create_folder(settings.DVBLAST_SOCKETS_DIR)
        create_folder(settings.DVBLAST_LOGS_DIR)

    def _clean_sock_file(self):
        self.server.execute('/bin/rm -f %s%d.sock' % (
            settings.DVBLAST_SOCKETS_DIR, self.pk)
        )

    def _read_ctl(self, command):
        "Returns an etree object containing dvblast status information"
        from lxml import etree
        ret = self.server.execute('%s -x xml -r %s%d.sock %s' % (
            settings.DVBLASTCTL_COMMAND,
            settings.DVBLAST_SOCKETS_DIR,
            self.pk,
            command)
        )
        return etree.fromstring(" ".join(ret))

    def has_lock(self):
        "Return True if is successfully tuned"
        has_lock = False
        # This will throw and exception if the device couldn't tune
        try:
            status = self._read_ctl('fe_status')
            if status.find('.//STATUS[@status="HAS_LOCK"]') is not None:
                has_lock = True
        except:
            pass
        return has_lock

    def tuned(self):
        if self.running() is False:
            return u''
        if self.has_lock() is True:
            return u'<a style="color:green;">OK</a>'
        else:
            return u'<a style="color:red;">Sem sinal</a>'
    tuned.short_description = _(u'Sinal')
    tuned.allow_tags = True

    def scan(self):
        "Scans the transport stream and creates DemuxedInputs accordingly"
        import time
        if self.status or self.running():
            was_running = True
        else:
            was_running = False
            self.start()
        time.sleep(3)  # TODO: Improve this
        if self.has_lock() is False:
            raise InputModel.GotNoLockException("%s" % self)
        pat = self._read_ctl('get_pat')
        programs = pat.findall('.//PROGRAM')
        sdt = self._read_ctl('get_sdt')
        services = []
        for program in programs:
            number = int(program.get('number'))
            if number is 0:
                continue  # Program 0 never works
            ct = ContentType.objects.get_for_model(self)
            service, created = \
                DemuxedService.objects.get_or_create(server=self.server,
                    sid=number, content_type=ct, object_id=self.pk)
            detail = \
                sdt.find('.//SERVICE[@sid="%d"]/DESC/SERVICE_DESC' % number)
            if detail is not None:
                service.provider = detail.get('provider')
                service.service_desc = detail.get('service')
                service.save()
            services.append(service)
        if was_running is False:
            self.stop()
        return services


class DigitalTunerHardware(models.Model):

    server = models.ForeignKey(Server)
    id_vendor = models.CharField(max_length=100)
    id_product = models.CharField(max_length=100)
    bus = models.CharField(max_length=100)
    driver = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now=True)
    uniqueid = models.CharField(max_length=100, unique=True, null=True)
    adapter_nr = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('server', 'adapter_nr')

    def __unicode__(self):
        return '[%s:%s] Bus: %s, Adapter: %s, Driver: %s, ID: %s' % (
            self.id_vendor, self.id_product, self.bus,
            self.adapter_nr, self.driver, self.uniqueid)

    def _read_mac_from_dvbworld(self):
        if self.id_vendor == '04b4':
            self.server.execute('/usr/bin/sudo /usr/bin/dvbnet -a %s -p 100'
                            % self.adapter_nr, persist=True)
            mac = self.server.execute('/sbin/ifconfig dvb%s_0 | '
                            'grep -o -E "([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"'
                                % self.adapter_nr, persist=True)
            self.server.execute('/usr/bin/sudo /usr/bin/dvbnet -d %s'
                                % self.adapter_nr)
            return " ".join(mac).strip()
        else:
            raise Exception('This adapter is not from DVBWorld: %s' % self)

    def grab_info(self):
        "Connects to server and grab some information to fill in the object"
        import re
        udevadm = '/sbin/udevadm'
        # Sanity check
        log = logging.getLogger('debug')
        log.debug('grab_info: server=%s, adapter_nr=%s' % (self.server,
            self.adapter_nr))
        if self.server is None or self.adapter_nr is None:
            raise Exception('server and adapter_nr attributes '
                                'must both be pre-defined.')
        # Connect to server and obtain data
        try:
            self.server.execute('/bin/ls /dev/dvb/adapter%s' % self.adapter_nr,
                                    persist=True)
        except Server.ExecutionFailure:  # The file don't exist
            return
        info = " ".join(
            self.server.execute("%s info -a -p "
            "$(%s info -q path -n /dev/dvb/adapter%s/frontend0)" % (
            udevadm, udevadm, self.adapter_nr), persist=True
            )
        )
        match = re.search(r'ATTRS\{idVendor\}=="([0-9a-fA-F]+)"', info)
        self.id_vendor = match.groups()[0]
        match = re.search(r'ATTRS\{idProduct\}=="([0-9a-fA-F]+)"', info)
        self.id_product = match.groups()[0]
        match = re.search(r'KERNELS=="(.*)"', info)
        self.bus = match.groups()[0]
        match = re.search(r'ATTRS\{devnum\}=="(\d+)"', info)
        devnum = match.groups()[0]
        try:
            ret = self.server.execute(
                '/usr/bin/lsusb -t | /bin/grep "Dev %s"' % devnum)
            match = re.search(r'Driver=(.*),', " ".join(ret))
            self.driver = match.groups()[0]
        except Server.ExecutionFailure:
            "Se foi, foi. Se não foi, tudo bem."
            pass

        if self.id_vendor == '04b4':
            self.uniqueid = self._read_mac_from_dvbworld()


class DigitalTuner(InputModel, DeviceServer):
    class Meta:
        abstract = True

    frequency = models.PositiveIntegerField(_(u'Frequência'), help_text=u'MHz')
    src = generic.GenericRelation(DemuxedService)

    class AdapterNotInstalled(Exception):
        pass

    def _get_cmd(self):
        cmd = u' -w'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        return cmd

    def start(self, adapter_num=None):
        "Starts a dvblast instance based on the current model's configuration"
        super(DigitalTuner, self).start()
        cmd = self._get_cmd(adapter_num)
        conf = self._get_config()
        # Create the necessary folders
        self._create_folders()
        # Write the config file to disk
        self.server.execute('echo "%s" > %s%d.conf' % (conf,
                        settings.DVBLAST_CONFS_DIR, self.pk), persist=True)
        if self.status is True:
            # Already running, just reload config
            self.reload_config()
        else:
            # Cleanup residual sock file if applyable
            self._clean_sock_file()
            # Start dvblast process
            log_path = '%s%d' % (settings.DVBLAST_LOGS_DIR, self.pk)
            self.pid = self.server.execute_daemon(cmd, log_path=log_path)
            self.status = True
            self.save()


class DvbTuner(DigitalTuner):
    class Meta:
        verbose_name = _(u'Sintonizador DVB-S/S2')
        verbose_name_plural = _(u'Sintonizadores DVB-S/S2')

    MODULATION_CHOICES = (
        (u'QPSK', u'QPSK'),
        (u'8PSK', u'8-PSK'),
    )
    POLARIZATION_CHOICES = (
        (u'H', _(u'Horizontal (H)')),
        (u'V', _(u'Vertical (V)')),
        (u'R', _(u'Direita (R)')),
        (u'L', _(u'Esquerda (L)')),
    )
    FEC_CHOICES = (
        (u'0', u'Off'),
        (u'12', u'1/2'),
        (u'23', u'2/3'),
        (u'34', u'3/4'),
        (u'35', u'3/5'),
        (u'56', u'5/6'),
        (u'78', u'7/8'),
        (u'89', u'8/9'),
        (u'910', u'9/10'),
        (u'999', u'Auto'),
    )
    symbol_rate = models.PositiveIntegerField(_(u'Taxa de símbolos'),
        help_text=u'Msym/s')
    modulation = models.CharField(_(u'Modulação'),
        max_length=200, choices=MODULATION_CHOICES)
    polarization = models.CharField(_(u'Polarização'),
        max_length=200, choices=POLARIZATION_CHOICES)
    fec = models.CharField(_(u'FEC'),
        max_length=200, choices=FEC_CHOICES, default=u'999')
    adapter = models.CharField(_(u'Adaptador'), max_length=200,
        null=True, blank=True)
    antenna = models.ForeignKey(Antenna, verbose_name=_(u'Antena'))

    def __unicode__(self):
        return '%s - %d %s %d' % (
            self.antenna, self.frequency, self.polarization, self.symbol_rate)

    @property
    def adapter_num(self):
        try:
            adapter = DigitalTunerHardware.objects.get(
                                server=self.server, uniqueid=self.adapter)
        except DigitalTunerHardware.DoesNotExist:
            # Log something and...
            raise DvbTuner.AdapterNotInstalled(
                _(u'The DVBWorld tuner "%s" is not ' \
                  u'installed on server "%s"' % (self.adapter, self.server)))
        return adapter.adapter_nr

    def _get_cmd(self, adapter_num=None):
        # Get tuning parameters
        cmd = u'%s' % settings.DVBLAST_COMMAND
        if self.antenna.lnb_type == 'multiponto_c':
            cmd += ' -f %d000' % (self.frequency - 600)
        else:
            cmd += ' -f %d000' % self.frequency
            if self.polarization == 'V':
                cmd += ' -v 13'
            elif self.polarization == 'H':
                cmd += ' -v 18'
            else:
                raise NotImplementedError
        if self.modulation == '8PSK':
            cmd += ' -m psk_8'
        cmd += ' -s %d000 -F %s' % (self.symbol_rate, self.fec)
        if adapter_num is None:
            cmd += ' -a %s' % self.adapter_num
        else:
            cmd += ' -a %s' % adapter_num
        cmd += super(DvbTuner, self)._get_cmd()

        return cmd


class IsdbTuner(DigitalTuner):
    "http://pt.wikipedia.org/wiki/SBTVD"
    class Meta:
        verbose_name = _(u'Sintonizador ISDB-Tb')
        verbose_name_plural = _(u'Sintonizadores ISDB-Tb')

    MODULATION_CHOICES = (
        (u'qam', u'QAM'),
    )

    modulation = models.CharField(_(u'Modulação'),
        max_length=200, choices=MODULATION_CHOICES, default=u'qam')
    bandwidth = models.PositiveSmallIntegerField(_(u'Largura de banda'),
        null=True, help_text=u'MHz', default=6)
    adapter = models.PositiveSmallIntegerField(null=True)

    def __unicode__(self):
        return str(self.frequency)

    def start(self, adapter_num=None):
        if adapter_num is None:
            self.adapter = self.adapter_num
        else:
            self.adapter = adapter_num
        super(IsdbTuner, self).start(adapter_num)

    def stop(self):
        self.adapter = None
        super(IsdbTuner, self).stop()

    @property
    def adapter_num(self):
        "Return an adapter number that is not being used at the moment"
        adapters = DigitalTunerHardware.objects.filter(
            server=self.server, id_vendor='1554')
        if adapters.count() > 0:
            for adapter in adapters:
                if not IsdbTuner.objects.filter(server=self.server,
                        adapter=adapter.adapter_nr).exists():
                    return adapter.adapter_nr

        raise IsdbTuner.AdapterNotInstalled(
            _(u'There is no PixelView tuner available ' \
              u'on server "%s"' % self.server))

    def _get_cmd(self, adapter_num=None):
        cmd = u'%s' % settings.DVBLAST_COMMAND
        cmd += ' -f %d000' % self.frequency
        if self.modulation == 'qam':
            cmd += ' -m qam_auto'
        cmd += ' -b %d' % self.bandwidth
        if adapter_num is None:
            cmd += ' -a %d' % self.adapter_num
        else:
            cmd += ' -a %d' % adapter_num
        cmd += super(IsdbTuner, self)._get_cmd()

        return cmd


class IPInput(InputModel, DeviceServer):
    "Generic IP input class"
    class Meta:
        abstract = True

    PROTOCOL_CHOICES = (
                        (u'udp', u'UDP'),
                        (u'rtp', u'RTP'),
                        )

    interface = models.ForeignKey(NIC, verbose_name=_(u'Interface de rede'))
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    protocol = models.CharField(_(u'Protocolo de transporte'), max_length=20,
                                choices=PROTOCOL_CHOICES, default=u'udp')
    src = generic.GenericRelation(DemuxedService)

    def start(self):
        cmd = self._get_cmd()
        conf = self._get_config()
        # Create the necessary folders
        self._create_folders()
        # Write the config file to disk
        self.server.execute('echo "%s" > %s%d.conf' % (conf,
            settings.DVBLAST_CONFS_DIR, self.pk), persist=True)
        # Cleanup residual sock file if applyable
        self._clean_sock_file()
        # Start dvblast process
        log_path = '%s%d' % (settings.DVBLAST_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(cmd, log_path=log_path)
        self.status = True
        self.save()


class UnicastInput(IPInput):
    "Unicast MPEG2TS IP input stream"
    class Meta:
        verbose_name = _(u'Entrada IP unicast')
        verbose_name_plural = _(u'Entradas IP unicast')

    def __unicode__(self):
        return '%d [%s]' % (self.port, self.interface)

    def validate_unique(self, exclude=None):
        # unique_together = ('port', 'interface', 'server')
        from django.core.exceptions import ValidationError
        val = UnicastInput.objects.filter(port=self.port,
                                          interface=self.interface,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _(u'Combinação já existente: %s e %d e %s' % (
                self.server.name, self.port, self.interface))
            raise ValidationError({'__all__': [msg]})

    def _get_cmd(self):
        cmd = u'%s' % settings.DVBLAST_COMMAND
        cmd += ' -D @%s:%d' % (self.interface.ipv4, self.port)
        if self.protocol == 'udp':
            cmd += '/udp'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        return cmd


class MulticastInput(IPInput):
    "Multicast MPEG2TS IP input stream"
    class Meta:
        verbose_name = _(u'Entrada IP multicast')
        verbose_name_plural = _(u'Entradas IP multicast')

    ip = models.IPAddressField(_(u'Endereço IP multicast'))

    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip, self.port, self.interface)

    def validate_unique(self, exclude=None):
        # unique_together = ('ip', 'server')
        from django.core.exceptions import ValidationError
        val = MulticastInput.objects.filter(ip=self.ip,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _(u'Combinação já existente: %s e %s' % (
                self.server.name, self.ip))
            raise ValidationError({'__all__': [msg]})

    def _get_cmd(self):
        cmd = u'%s' % settings.DVBLAST_COMMAND
        cmd += ' -D @%s:%d' % (self.ip, self.port)
        if self.protocol == 'udp':
            cmd += '/udp'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        return cmd


@receiver(pre_save, sender=MulticastInput)
def MulticastInput_pre_save(sender, instance, **kwargs):
    "Signal to create the route"
    server = instance.server
    if server.offline_mode:
        return
    # If it already exists, delete
    try:
        obj = MulticastInput.objects.get(pk=instance.pk)
        ip = obj.ip
        dev = server.get_netdev(obj.interface.ipv4)
        server.delete_route(ip, dev)
    except MulticastInput.DoesNotExist:
        pass

    # Create a new rote
    ip = instance.ip
    dev = server.get_netdev(instance.interface.ipv4)
    server.create_route(ip, dev)


@receiver(pre_delete, sender=MulticastInput)
def MulticastInput_pre_delete(sender, instance, **kwargs):
    "Signal to delete the route"
    server = instance.server
    if server.offline_mode:
        return
    ip = instance.ip
    dev = server.get_netdev(instance.interface.ipv4)
    server.delete_route(ip, dev)


class FileInput(DeviceServer):
    """
    VLC streaming device.
    file -> vlc -> output -> ip
    """
    class Meta:
        verbose_name = _(u'Arquivo de entrada')
        verbose_name_plural = _(u'Arquivos de entrada')

    filename = models.CharField(
        _(u'Arquivo de origem'),
        max_length=255,
        blank=True,
        null=True)
    repeat = models.BooleanField(_(u'Repetir indefinidamente'), default=True)
    src = generic.GenericRelation(UniqueIP)

    def __unicode__(self):
        if hasattr(self, 'server') is False:
            return self.description
        return '[%s] %s -->' % (self.server, self.description)

    def _get_cmd(self):
        ip = self.src.get()
        cmd = u'%s' % settings.VLC_COMMAND
        cmd += ' -I dummy -v'
        if self.repeat:
            cmd += ' -R'
        #cmd += ' "%s%s"' % (settings.VLC_VIDEOFILES_DIR, self.filename)
        cmd += ' "%s"' % (self.filename)
        cmd += ' --sout "#std{access=udp,mux=ts,dst=%s:%d}"' % (
            ip.ip, ip.port)
        return cmd

    def start(self, recursive=False):
        """Inicia processo do VLC"""
        self.pid = self.server.execute_daemon(self._get_cmd())
        self.status = True
        self.save()
        return self.status


class OutputModel(models.Model):
    "Each model of output type should inherit this"
    class Meta:
        abstract = True

    content_type = models.ForeignKey(ContentType,
        #limit_choices_to={"model__in": ("UniqueIP",)},
        null=True,
        verbose_name=_(u'Conexão com device'))
    object_id = models.PositiveIntegerField(null=True)
    sink = generic.GenericForeignKey()

    def _create_folders(self):
        "Creates all the folders multicat needs"
        def create_folder(path):
            try:
                self.server.execute('/usr/bin/sudo /bin/mkdir -p %s' % path)
                self.server.execute('/usr/bin/sudo /bin/chown %s:%s %s' % (
                    self.server.username, self.server.username, path))
            except Exception as ex:
                log = logging.getLogger('debug')
                log.error(unicode(ex))
        create_folder(settings.MULTICAT_SOCKETS_DIR)
        create_folder(settings.CHANNEL_RECORD_DIR)
        create_folder(settings.MULTICAT_LOGS_DIR)

    def stop(self, recursive=False):
        super(OutputModel, self).stop()
        if recursive is True:
            self.sink.stop(recursive=recursive)


class IPOutput(OutputModel, DeviceServer):
    "Generic IP output class"
    class Meta:
        abstract = True

    PROTOCOL_CHOICES = (
                        (u'udp', u'UDP'),
                        (u'rtp', u'RTP'),
                        )

    interface = models.ForeignKey(NIC,
        verbose_name=_(u'Interface de rede externa'))
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    protocol = models.CharField(_(u'Protocolo de transporte'), max_length=20,
        choices=PROTOCOL_CHOICES, default=u'udp')

    def start(self, recursive=False):
        # Create the necessary folders
        self._create_folders()
        # Start multicat
        log_path = '%s%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(),
            log_path=log_path)
        self.status = True
        self.save()
        if recursive is True:
            self.sink.start(recursive=recursive)


class MulticastOutput(IPOutput):
    "Multicast MPEG2TS IP output stream"
    class Meta:
        verbose_name = _(u'Saída IP multicast')
        verbose_name_plural = _(u'Saídas IP multicast')

    ip = models.IPAddressField(_(u'Endereço IP multicast'), unique=True)
    nic_sink = models.ForeignKey(NIC, related_name='nic_sink',
        verbose_name=_(u'Interface de rede interna'))

    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip, self.port, self.interface)

    def natural_key(self):
        return {'ip': self.ip, 'port': self.port}

#    def validate_unique(self, exclude=None):
#        # unique_together = ('ip', 'server')
#        from django.core.exceptions import ValidationError
#        val = MulticastOutput.objects.filter(ip_out=self.ip_out,
#            server=self.server)
#        if val.exists() and val[0].pk != self.pk:
#            msg = _(u'Combinação já existente: %s e %s' % (
#                self.server.name, self.ip))
#            raise ValidationError({'__all__': [msg]})

    def _get_cmd(self):
        cmd = u'%s' % settings.MULTICAT_COMMAND
        cmd += ' -c %s%d.sock' % (settings.MULTICAT_SOCKETS_DIR, self.pk)
        cmd += ' -u @%s:%d/ifaddr=%s' % (
            self.sink.ip, self.sink.port, self.nic_sink.ipv4)
        if self.protocol == 'udp':
            cmd += ' -U'
        cmd += ' %s:%d@%s' % (self.ip, self.port, self.interface.ipv4)
        return cmd


## Gravação:
# RT=$((60*60*27000000)) #rotate (minutos)
# FOLDER=ch_53
# MULTICAT -r $RT -u @239.0.1.1:10000 $FOLDER
# /usr/bin/multicat -c /var/run/multicat/sockets/record_6.sock -u \
#@239.10.0.1:10000/ifaddr=172.17.0.1 -U -r 97200000000 -u /iptv/recorder/6
class StreamRecorder(OutputModel, DeviceServer):
    u"""
    Serviço de gravação dos fluxos multimidia.
    """
    rotate = models.PositiveIntegerField(_(u'Tempo em minutos do arquivo'),
        help_text=_(u'Padrão é 60 min.'), default=60)
    folder = models.CharField(_(u'Diretório destino'), max_length=500,
        default=settings.CHANNEL_RECORD_DIR, )
    keep_time = models.PositiveIntegerField(_(u'Horas que permanece gravado'),
        help_text=_(u'Padrão: 48'), default=48)
    start_time = models.DateTimeField(_(u'Hora inicial da gravação'),
        null=True, default=None, blank=True)
    channel = models.ForeignKey('tv.Channel', null=True, blank=True)
    nic_sink = models.ForeignKey(NIC,
        verbose_name=_(u'Interface de rede interna'))

    class Meta:
        verbose_name = _(u'Gravador de fluxo')
        verbose_name_plural = _(u'Gravadores de fluxo')

    def __unicode__(self):
        return u'id:%d rotate:%d, keep:%d, channel:%s, start:%s' % (
            self.id, self.rotate,
            self.keep_time, self.channel, self.start_time)

    def _get_cmd(self):
        # Create the necessary folders
        #self._create_folders()
        # Create folder to store record files
        self.server.execute('mkdir -p %s/%d' % (self.folder, self.pk))
        # /usr/bin/multicat -c /var/run/multicat/sockets/record_6.sock -u \
        #@239.10.0.1:10000/ifaddr=172.17.0.1 -U -r 97200000000 \
        #-u /iptv/recorder/6
        cmd = u'%s -r %d -U -u @%s:%d/ifaddr=%s %s/%d' % (
            settings.MULTICAT_COMMAND,
            (self.rotate * 60 * 27000000),
            self.sink.ip,
            self.sink.port,
            self.nic_sink.ipv4,
            self.folder,
            self.pk
            )
        return cmd

    def start(self, recursive=False):
        # Create destination folder
        # Create the necessary log folders
        #self._create_folders()
        # Start multicat
        log_path = '%s%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(),
            log_path=log_path)
        if self.pid > 0:
            import datetime
            self.start_time = datetime.datetime.now()
            self.status = True
        self.save()
        if recursive is True:
            self.sink.start(recursive=recursive)
        # This install all cronjobs to current recorder server
        self.install_cron()

    def get_cron_line(self):
        r"Install cronjob to clean expired record"
        # Example of job definition:
        # .---------------- minute (0 - 59)
        # |  .------------- hour (0 - 23)
        # |  |  .---------- day of month (1 - 31)
        # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
        # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7)
        # |  |  |  |  |
        # *  *  *  *  * user-name  command to be executed
        #*/30 * * * * nginx /iptv/bin/multicat_expire.sh /iptv/recorder/50/ 13
        #*/30 * * * * nginx /iptv/bin/multicat_expire.sh /iptv/recorder/53/ 13
        #*/30 * * * * nginx /iptv/bin/multicat_expire.sh /iptv/recorder/54/ 25
        #import getpass
        #user = getpass.getuser()
        elements = (self.keep_time / (self.rotate / 60)) + 1
        cmd = '*/30 * * * * %s %s/%d/ %d' % (
            settings.CHANNEL_RECORD_CLEAN_COMMAND, self.folder, self.id,
            elements)
        return cmd

    def install_cron(self):
        u'Reinstall crontab for current server\
        (for now full install all recorders)'
        from tempfile import NamedTemporaryFile
        from datetime import datetime
        # Get all running recorders on current recorder server
        recorders = StreamRecorder.objects.filter(
            server=self.server, status=True)
        if len(recorders) == 0:
            return
        tmpfile = NamedTemporaryFile()
        cron = '# New cronfile: %s \n\n' % datetime.now()
        remote_tmpfile = "".join(self.server.execute('/bin/mktemp')).strip()
        for rec in recorders:
            cron += '# recorder = %s\n' % rec
            cron += rec.get_cron_line() + '\n\n'
        tmpfile.file.write(cron)
        tmpfile.file.flush()
        if self.server.offline_mode is False:
            self.server.put(tmpfile.name, remote_tmpfile)
        self.server.execute('/usr/bin/crontab %s ' % remote_tmpfile)
        tmpfile.close()


## Recuperação:
# TIME_SHIFT=-$(( 60 * 5 * 27000000 )) # (minutos)
# FOLDER=ch_53
# MULTICAT -U -k $TIME_SHIFT $FOLDER 192.168.0.244:5000
# /usr/bin/multicat -r 97200000000 -k -$(( 27000000 * 60  * 5)) \
#-U /iptv/recorder/6 192.168.0.244:10000
class StreamPlayer(OutputModel, DeviceServer):
    u"""Player de conteúdo gravado nos servidores (catshup-TV)"""
    recorder = models.ForeignKey(StreamRecorder)
    """Client IP address"""
    stb_ip = models.IPAddressField(_(u'IP destino'), db_index=True,
        unique=True)
    stb_port = models.PositiveSmallIntegerField(_(u'Porta destino'),
        help_text=_(u'Padrão: %s' % (settings.CHANNEL_PLAY_PORT)),
        default=settings.CHANNEL_PLAY_PORT)
    # Socket de controle do aplicativo no servidor
    control_socket = models.CharField(_(u'Socket de controle (auto)'),
        max_length=500)

    class Meta:
        verbose_name = _(u'Reprodutor de fluxo gravado')
        verbose_name_plural = _(u'Reprodutores de fluxo gravado')

    def play(self, time_shift=0):
        ur"""
        Localizar um servidor de gravação que tenha o canal gravado no horário
        solicitado.
        Caso esteja rodando um vídeo anterior, interromper este antes de
        executar o novo.
        """
        if self.status and self.pid:
            self.stop()
        return self.start(time_shift=time_shift)

    def pause(self):
        """
        Abre o socket da reprodução atual chamando o multicatctl e envia o
        comando pause para o soket específico
        multicatctl -c /xxx/multicat_yy.socket pause
        """
        pass

    def _get_cmd(self, time_shift=0):
        self.control_socket = '%sclient_%d.sock' % (
            settings.MULTICAT_SOCKETS_DIR,
            self.pk)
        cmd = u'%s -c %s -r %s -k -%s -U %s/%d %s:%d' % (
            settings.MULTICAT_COMMAND,
            self.control_socket,
            (self.recorder.rotate * 60 * 27000000),
            (time_shift * 27000000),
            self.recorder.folder,
            self.recorder.pk,
            self.stb_ip,
            self.stb_port
            )
        return cmd

    def start(self, recursive=False, time_shift=0):
        # Create destination folder
        # Create the necessary log folders
        #self._create_folders()
        # Start multicat
        log = logging.getLogger('debug')
        log_path = '%splayer_%d' % (settings.MULTICAT_LOGS_DIR, self.id)
        cmd = self._get_cmd(time_shift=time_shift)
        log.info('StreamPlayer.command:%s' % cmd)
        self.pid = self.server.execute_daemon(cmd, log_path=log_path)
        self.status = True
        self.save()
