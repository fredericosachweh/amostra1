#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from __future__ import division, unicode_literals
import logging
from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

#from client.models import SetTopBox

conn = {}


class AbstractServer(models.Model):
    """
    Servidor e caracteristicas de conexão.
    """

    name = models.CharField(_('Nome'), max_length=200, unique=True)
    host = models.IPAddressField(_('Host'), blank=True, unique=True)
    username = models.CharField(_('Usuário'), max_length=200, blank=True)
    password = models.CharField(_('Senha'), max_length=200, blank=True)
    rsakey = models.CharField(_('Chave RSA'),
        help_text='Exemplo: ~/.ssh/id_rsa',
        max_length=500,
        blank=True)
    ssh_port = models.PositiveSmallIntegerField(_('Porta SSH'),
        blank=True, null=True, default=22)
    modified = models.DateTimeField(_('Última modificação'), auto_now=True)
    status = models.BooleanField(_('Status'), default=False)
    msg = models.TextField(_('Mensagem de retorno'), blank=True)
    offline_mode = models.BooleanField(default=False)
    _is_offline = False

    class Meta:
        abstract = True
        verbose_name = _('Servidor de Recursos')
        verbose_name_plural = _('Servidores de Recursos')

    class ExecutionFailure(Exception):
        pass

    class InvalidOperation(Exception):
        pass

    def __unicode__(self):
        return '%s' % (self.name)

    def connect(self):
        """Conecta-se ao servidor"""
        from lib import ssh
        log = logging.getLogger('device.remotecall')
        if self.offline_mode:
            raise Server.InvalidOperation(
                "Shouldn't connect when offline mode is set")
        log.debug('conn:%s', conn)
        c = conn.get(self.host)
        if c is not None:
            log.debug('ssh:%s', c)
            if c._transport_live:
                return c
            else:
                c = ssh.Connection(host=self.host,
                    port=self.ssh_port,
                    username=self.username,
                    password=self.password,
                    private_key=self.rsakey)
                conn[self.host] = c
        try:
            log.debug('ssh new:%s', self)
            conn[self.host] = ssh.Connection(host=self.host,
                port=self.ssh_port,
                username=self.username,
                password=self.password,
                private_key=self.rsakey)
            self.status = True
            self._is_offline = False
            self.msg = 'OK'
        except Exception as ex:
            log = logging.getLogger('device.remotecall')
            log.error('%s(%s:%s %s):%s' % (self, self.host, self.ssh_port,
                self.username, ex))
            self.status = False
            self.disconect()
            self._is_offline = True
            self.msg = ex
        self.save()
        return conn.get(self.host)

    def disconect(self):
        c = conn.get(self.host)
        if c is not None:
            c.close()

    def execute(self, command, persist=True, check=True):
        """Executa um comando no servidor"""
        log = logging.getLogger('device.remotecall')
        log.debug('[%s@%s]# %s', self.username, self.name, command)
        try:
            s = self.connect()
            self.msg = 'OK'
            self._is_offline = s is None
        except Exception as ex:
            self.msg = 'Can not connect:' + str(ex)
            log.error('[%s]:%s' % (self, ex))
            self._is_offline = True
            self.save()
            return 'Can not connect'
        log.debug('Offline=%s', self._is_offline)
        log.debug('Conn=%s', s)
        if self._is_offline:
            return 'Server is offline'
        ret = s.execute(command)
        if not persist and self.status:
            log.debug('Close BY  not persist and self.status')
            s.close()
        self.save()
        if ret.get('exit_code') and ret['exit_code'] is not 0 and check:
                raise Server.ExecutionFailure(
                    'Command "%s" returned status "%d" on server "%s": "%s"' %
                    (command, ret['exit_code'], self, u"".join(ret['output'])))
        return ret['output']

    def execute_daemon(self, command, log_path=None):
        "Excuta o processo em background (daemon)"
        log = logging.getLogger('device.remotecall')
        log.debug('[%s@%s]#(DAEMON) %s', self.username, self.name, command)
        try:
            s = self.connect()
            self.msg = 'OK'
            self._is_offline = False
        except Exception as ex:
            self.msg = ex
            self.status = False
            self._is_offline = True
            log.error('[%s]:%s' % (self, ex))
            raise ex
        ret = s.execute_daemon(command, log_path)
        exit_code = ret.get('exit_code')
        if exit_code is not 0:
            raise Server.ExecutionFailure(
                    'Command "%s" returned status "%d" on server "%s": "%s"' %
                    (command, ret['exit_code'], self, u"".join(ret['output'])))
        pid = ret.get('pid')
        #s.close()
        self.save()
        return int(pid)

    def get(self, remotepath, localpath=None):
        """Copies a file between the remote host and the local host."""
        s = self.connect()
        s.get(remotepath, localpath)
        #s.close()

    def put(self, localpath, remotepath=None):
        """Copies a file between the local host and the remote host."""
        s = self.connect()
        s.put(localpath, remotepath)
        #s.close()

    def process_alive(self, pid):
        "Verifica se o processo está em execução no servidor"
        log = logging.getLogger('debug')
        if self._is_offline:
            return False
        for p in self.list_process(pid):
            if p['pid'] == pid:
                log.info('Process [%d] live on [%s] = True', pid, self)
                return True
        log.info('Process [%d] live on [%s] = False', pid, self)
        return False

    def list_process(self, pid=None):
        """
        Retorna a lista de processos rodando no servidor
        """
        ps = '/bin/ps -eo pid,comm,args'
        if pid is not None:
            ps = '/bin/ps -o pid,comm,args -p %i' % pid
            stdout = self.execute(ps, persist=True, check=False)
        else:
            stdout = self.execute(ps, persist=True)
        ret = []
        if self._is_offline:
            return ret
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
        #s.close()
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
        log.info('---|-Auto create NIC on %s', self)
        nics = []
        for iface in self._list_interfaces():
            nnics = NIC.objects.filter(name=iface['dev'], server=self).count()
            if nnics == 0:
                nic = NIC.objects.create(name=iface['dev'], server=self,
                    ipv4=iface['ip'])
                log.info('   |-New NIC found %s', nic)
            else:
                nic = NIC.objects.get(name=iface['dev'], server=self)
                nic.ipv4 = iface['ip']
                log.info('   |-Existing NIC %s', nic)
            nic.ipv4 = iface['ip']
            nic.save()
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
        content = ''.join(ret)
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

    def show_versions(self):
        if self.id is None:
            return ''
        pkgs = settings.RPM_CHECK_VERSION
        rpm_cmd = u"export LANG=c && rpmquery --queryformat '%%{name} \
%%{version}-%%{release} (%%{ARCH}) %%{BUILDTIME:date}\\n' %s | grep -v 'not installed'" % (pkgs)
        # %%{release} %%{installtime:date}
        response = self.execute(rpm_cmd)
        html = [i.strip() for i in response]
        return '<br>'.join(html)

    show_versions.allow_tags = True
    show_versions.short_description = 'Versões'


class Server(AbstractServer):
    SERVER_TYPE_CHOICES = [
        ('local', _('Servidor local DEMO')),
        ('dvb', _('Sintonizador DVB')),
        ('recording', _('Servidor TVoD')),
        ('nbridge', _('Servidor NBridge')),
    ]

    server_type = models.CharField(_('Tipo de Servidor'), max_length=100,
        choices=SERVER_TYPE_CHOICES)

    def switch_link(self):
        url = reverse('device.views.server_status', kwargs={'pk': self.id})
        return '<a href="%s" id="server_id_%s" >Atualizar</a>' % (url, self.id)

    switch_link.allow_tags = True
    switch_link.short_description = 'Status'


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
    name = models.CharField(_('Interface de rede'), max_length=50)
    server = models.ForeignKey(Server)
    ipv4 = models.IPAddressField(_('Endereço ip v4 atual'))

    class Meta:
        unique_together = ('name', 'server')

    def __unicode__(self):
        return '[%s] %s (%s)' % (self.server, self.name, self.ipv4)


class UniqueIP(models.Model):
    """
    Classe de endereço ip externo (na rede dos clientes)
    """
    class Meta:
        ordering = ('ip', )
        verbose_name = _('Endereço IPv4 multicast')
        verbose_name_plural = _('Endereços IPv4 multicast')
    ip = models.IPAddressField(_('Endereço IP'),
        unique=True,
        null=True)
    port = models.PositiveSmallIntegerField(_('Porta'), default=10000)
    #nic = models.ForeignKey(NIC)
    sequential = models.PositiveSmallIntegerField(
        _('Valor auxiliar para gerar o IP único'),
        default=2)

    ## Para o relacionamento genérico de origem
    sink = generic.GenericForeignKey()
    content_type = models.ForeignKey(ContentType,
        limit_choices_to={"model__in": (
            "demuxedservice", "fileinput", "softtranscoder")},
        blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        if self.sink is None:
            sink = ''
            sink_classname = ''
        else:
            sink = self.sink
            sink_classname = self.sink.__class__.__name__
        src_connections = [unicode(con) for con in self.src]
        ret = '%s %s --> [ %s:%d ] <-- { %s }' % (
            sink_classname, sink, self.ip,
            self.port, ", ".join(src_connections),
        )
        return ret

    def sink_str(self):
        if self.sink is None:
            return ''
        return '<a href="%s">&lt;%s&gt; %s</a>' % (
            reverse('admin:device_%s_change' % self.sink._meta.module_name,
                args=[self.sink.pk]), self.sink._meta.verbose_name, self.sink)
    sink_str.allow_tags = True
    sink_str.short_description = _('Entrada (sink)')

    def src_str(self):
        if len(self.src) is 0:
            return ''
        ret = []
        for obj in self.src:
            ret.append('<a href="%s">&lt;%s&gt; %s</a>' % (
                reverse('admin:device_%s_change' % obj._meta.module_name,
                    args=[obj.pk]), obj._meta.verbose_name, obj))
        return u"<br />".join(ret)
    src_str.allow_tags = True
    src_str.short_description = _('Saídas (src)')

    @property
    def src(self):
        from itertools import chain
        uniqueip_type = ContentType.objects.get_for_model(UniqueIP)
        ipout = MulticastOutput.objects.filter(content_type=uniqueip_type,
                                               object_id=self.pk)
        recorder = StreamRecorder.objects.filter(content_type=uniqueip_type,
                                               object_id=self.pk)
        soft_transcoder = SoftTranscoder.objects.filter(
            content_type=uniqueip_type, object_id=self.pk)
        return list(chain(ipout, recorder, soft_transcoder))

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
        ip = settings.INTERNAL_IP_MASK % (
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
        log = logging.getLogger('debug')
        log.debug('UniqueIP.start args=%s, kwargs=%s', args, kwargs)
        if self.sink.running() is False:
            if kwargs.get('recursive') is True:
                self.sink.start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        log = logging.getLogger('debug')
        src = self.src
        log.debug('UniqueIP.stop args=%s, kwargs=%s, src:%s',
            args, kwargs, src)
        if kwargs.get('recursive') is True:
            if self.sink.running() is True:
                running = 0
                for sink in src:
                    if sink.status == True:
                        running += 1
                log.debug('Total running:%d', running)
                if running == 0:
                    for sink in src:
                        if sink.status == True:
                            sink.stop(*args, **kwargs)
                    self.sink.stop(*args, **kwargs)

    def running(self):
        return self.sink.running()


class DeviceServer(models.Model):
    """
    Aplicativo que roda em um determinado servidor.
    O metodo start deve ser sobreescrito com o comando específico
    """
    server = models.ForeignKey(Server, verbose_name=_('Servidor de recursos'))
    status = models.BooleanField(_('Status'), default=False, editable=False)
    pid = models.PositiveSmallIntegerField(_('PID'),
        blank=True, null=True, editable=False)
    description = models.CharField(_('Descrição'), max_length=250, blank=True)

    class AlreadyRunning(Exception):
        pass

    class NotRunning(Exception):
        pass

    def _type(self):
        return _('undefined')

    def start(self, *args, **kwargs):
        log = logging.getLogger('debug')
        log.info('Iniciando device %s', self)

    def stop(self, *args, **kwargs):
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
        if self.status == True:
            alive = self.server.process_alive(self.pid)
        else:
            alive = False
        return alive

    def __unicode__(self):
        return '%s - %s' % (self.__class__, self.description)

    def switch_link(self):
        module_name = self._meta.module_name
        if (hasattr(self, 'src') and self.src is None) or \
           (hasattr(self, 'sink') and self.sink is None):
            return _('Desconfigurado')
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
    switch_link.short_description = 'Status'


@receiver(pre_delete, sender=DeviceServer)
def DeviceServer_pre_delete(sender, instance, **kwargs):
    log = logging.getLogger('debug')
    #log.debug('DELETE: DeviceServer=%s "%s"', instance, sender)
    if instance.status and instance.pid:
        log.debug('Force stop recursive on delete')
        instance.stop(recursive=True)


class Antenna(models.Model):
    class Meta:
        verbose_name = _('Antena parabólica')
        verbose_name_plural = _('Antenas parabólicas')

    LNBS = (
            ('normal_c', 'C Normal'),
            ('multiponto_c', 'C Multiponto'),
            ('universal_k', 'Ku Universal'),
            )

    satellite = models.CharField(_('Satélite'), max_length=200)
    lnb_type = models.CharField(_('Tipo de LNB'), max_length=200,
        choices=LNBS, help_text=_('Verificar o tipo de LNBf escrito ' \
                                  'no cabeçote da antena'))

    def __unicode__(self):
        return str(self.satellite)


class DemuxedService(DeviceServer):
    class Meta:
        verbose_name = _('Entrada demultiplexada')
        verbose_name_plural = _('Entradas demultiplexadas')

    sid = models.PositiveIntegerField(_('Programa'))
    provider = models.CharField(_('Provedor'), max_length=2000, null=True,
        blank=True)
    service_desc = models.CharField(_('Serviço'), max_length=2000, null=True,
        blank=True)
    enabled = models.BooleanField(default=False)
    src = generic.GenericRelation(UniqueIP)
    nic_src = models.ForeignKey(NIC, blank=True, null=True)
    # Sink (connect to a Tuner or IP input)
    content_type = models.ForeignKey(ContentType,
        limit_choices_to={"model__in":
            ("dvbtuner", "isdbtuner", "unicastinput", "multicastinput")},
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
            if kwargs.get('recursive') is True:
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
            return _('Desconfigurado')
        return super(DemuxedService, self).switch_link()
    switch_link.allow_tags = True
    switch_link.short_description = 'Status'

    def get_pcrpid(self):
        log = logging.getLogger('debug')
        pcrpid = None
        try:
            log.debug('loading pmt')
            pmt = self.sink._read_ctl('get_pmt %d' % self.sid)
            pcrpid = pmt.get('pcrpid')
            log.debug('pcrpid is %s', pcrpid)
        except Exception as ex:
            log.error('ERROR:%s', ex)
        return pcrpid


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
        conf = ''
        for service in self._list_enabled_services():
            if service.src.count() > 0:
                sid = service.sid
                ip = service.src.all()[0].ip
                port = service.src.all()[0].port
                nic = service.nic_src
                conf += '%s:%d' % (ip, port)
                if nic is not None:
                    conf += '@%s' % nic.ipv4
                # Assume internal IPs always work under raw UDP
                conf += '/udp 1 %d\n' % sid

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

    def stop(self, *args, **kwargs):
        for service in self._list_enabled_services():
            service.stop()
        super(InputModel, self).stop()
        # Clean socket file
        path = '%s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        if self.server.file_exists(path):
            self.server.rm_file(path)

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
            return ''
        if self.has_lock() is True:
            return '<a style="color:green;">OK</a>'
        else:
            return '<a style="color:red;">Sem sinal</a>'
    tuned.short_description = _('Sinal')
    tuned.allow_tags = True

#DVBlastctl 2.2 (git-f91415d-dirty)
#Usage: dvblastctl -r <remote socket> [-x <text|xml>] [cmd]
#Options:
#  -r --remote-socket <name>       Set socket name to <name>.
#  -x --print <text|xml>           Choose output format for info commands.
#Control commands:
#  reload                          Reload configuration.
#  shutdown                        Shutdown DVBlast.
#Status commands:
#  fe_status                       Read frontend status information.
#  mmi_status                      Read CAM status.
#MMI commands:
#  mmi_slot_status <slot>          Read MMI slot status.
#  mmi_open <slot>                 Open MMI slot.
#  mmi_close <slot>                Close MMI slot.
#  mmi_get <slot>                  Read MMI slot.
#  mmi_send_text <slot> <text>     Send text to MMI slot.
#  mmi_send_choice <slot> <choice> Send choice to MMI slot.
#Demux info commands:
#  get_pat                         Return last PAT table.
#  get_cat                         Return last CAT table.
#  get_nit                         Return last NIT table.
#  get_sdt                         Return last SDT table.
#  get_pmt <service_id>            Return last PMT table.
#  get_pids                        Return info about all pids.
#  get_pid <pid>                   Return info for chosen pid only.
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
        try:
            sdt = self._read_ctl('get_sdt')
        except:
            pass
        services = []
        for program in programs:
            number = int(program.get('number'))
            if number is 0:
                continue  # Program 0 never works
            pmt = self._read_ctl('get_pmt %d' % number)
            #print(pmt)
            ct = ContentType.objects.get_for_model(self)
            service, created = \
                DemuxedService.objects.get_or_create(server=self.server,
                    sid=number, content_type=ct, object_id=self.pk)
            try:
                detail = sdt.find(
                    './/SERVICE[@sid="%d"]/DESC/SERVICE_DESC' % number)
            except:
                detail = None
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
        if self.id_vendor in ['04b4', '1131']:
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
        #log.info('INFO:%s', info)
        # ATTRS\{(i?d?[vV])endor\}=="(0x?)([0-9a-fA-F]{4}+)"
        match = re.search(
            r'ATTRS\{(idVendor|vendor)\}=="([0x]{2}|)([0-9a-fA-F]{4})"',
            info)
        # ATTRS\{(i?d?[vV])endor\}=="([0x]?)([0-9a-fA-F]{4})"
        # ATTRS\{(i?d?[vV])endor\}=="([0x]{2}|)([0-9a-fA-F]{4})"
        log.debug('vendor:%s', match.groups())
        self.id_vendor = match.groups()[2]
        match = re.search(
            r'ATTRS\{(idProduct|device)\}=="([0x]{2}|)([0-9a-fA-F]{4})"',
            info)
        if match is not None:
            log.debug('product:%s', match.groups())
            self.id_product = match.groups()[2]
        else:
            self.id_product = ''
        match = re.search(r'SUBSYSTEMS=="(.*)"', info)
        log.debug('SUBSYSTEMS:%s', match.groups())
        self.bus = match.groups()[0]
        if self.bus == 'usb':
            match = re.search(r'ATTRS\{devnum\}=="(\d+)"', info)
            if match is not None:
                log.debug('devnum:%s', match.groups())
                devnum = match.groups()[0]
            else:
                devnum = self.adapter_nr
            try:
                # lspci -k -b -d 1131:7160
                # Kernel modules: saa716x_tbs-dvb
                ret = self.server.execute(
                    '/usr/bin/lsusb -t | /bin/grep "Dev %s"' % devnum)
                match = re.search(r'Driver=(.*),', " ".join(ret))
                self.driver = match.groups()[0]
            except Server.ExecutionFailure as e:
                "Se foi, foi. Se não foi, tudo bem."
                log.error('CMD err:%s', e)
        else:
            try:
                # lspci -k -b -d 1131:7160
                # Kernel modules: saa716x_tbs-dvb
                ret = self.server.execute(
                    '/sbin/lspci -k -b -d %s:%s' % (self.id_vendor, self.id_product))
                #match = re.search(r'Kernel modules: (.*)', " ".join(ret))
                match = re.search(r'Kernel driver in use: (.*) TBS', " ".join(ret))
                self.driver = match.groups()[0]
            except Server.ExecutionFailure as e:
                "Se foi, foi. Se não foi, tudo bem."
                log.error('CMD err:%s', e)

        if self.id_vendor in ['04b4', '1131']:
            self.uniqueid = self._read_mac_from_dvbworld()


class DigitalTuner(InputModel, DeviceServer):
    class Meta:
        abstract = True

    frequency = models.PositiveIntegerField(_('Frequência'), help_text='MHz')
    src = generic.GenericRelation(DemuxedService)

    class AdapterNotInstalled(Exception):
        pass

    def _get_cmd(self):
        cmd = ' -w'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        return cmd

    def start(self, adapter_num=None, *args, **kwargs):
        "Starts a dvblast instance based on the current model's configuration"
        super(DigitalTuner, self).start(*args, **kwargs)
        cmd = self._get_cmd(adapter_num)
        conf = self._get_config()
        # Write the config file to disk
        self.server.execute('echo "%s" > %s%d.conf' % (conf,
            settings.DVBLAST_CONFS_DIR, self.pk), persist=True)
        if self.running() == True:
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
        verbose_name = _('Sintonizador DVB-S/S2')
        verbose_name_plural = _('Sintonizadores DVB-S/S2')

    MODULATION_CHOICES = (
        ('QPSK', 'QPSK'),
        ('8PSK', '8-PSK'),
    )
    POLARIZATION_CHOICES = (
        ('H', _('Horizontal (H)')),
        ('V', _('Vertical (V)')),
        ('R', _('Direita (R)')),
        ('L', _('Esquerda (L)')),
        ('U', _('Não especificada')),
    )
    FEC_CHOICES = (
        ('0', 'Off'),
        ('12', '1/2'),
        ('23', '2/3'),
        ('34', '3/4'),
        ('35', '3/5'),
        ('56', '5/6'),
        ('78', '7/8'),
        ('89', '8/9'),
        ('910', '9/10'),
        ('999', 'Auto'),
    )
    symbol_rate = models.PositiveIntegerField(_('Taxa de símbolos'),
        help_text='Msym/s')
    modulation = models.CharField(_('Modulação'),
        max_length=200, choices=MODULATION_CHOICES)
    polarization = models.CharField(_('Polarização'),
        max_length=200, choices=POLARIZATION_CHOICES)
    fec = models.CharField(_('FEC'),
        max_length=200, choices=FEC_CHOICES, default='999')
    adapter = models.CharField(_('Adaptador'), max_length=200,
        null=True, blank=True)
    antenna = models.ForeignKey(Antenna, verbose_name=_('Antena'))

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
                _('The DVBWorld tuner "%s" is not ' \
                  'installed on server "%s"' % (self.adapter, self.server)))
        return adapter.adapter_nr

    def _get_cmd(self, adapter_num=None):
        # Get tuning parameters
        cmd = '%s' % settings.DVBLAST_COMMAND
        if self.antenna.lnb_type == 'multiponto_c':
            cmd += ' -f %d000' % (self.frequency - 600)
        else:
            cmd += ' -f %d000' % self.frequency
            if self.polarization == 'V':
                cmd += ' -v 18'
            elif self.polarization == 'H':
                cmd += ' -v 13'
            elif self.polarization == 'U':
                pass
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
        verbose_name = _('Sintonizador ISDB-Tb')
        verbose_name_plural = _('Sintonizadores ISDB-Tb')

    MODULATION_CHOICES = (
        ('qam', 'QAM'),
    )

    modulation = models.CharField(_('Modulação'),
        max_length=200, choices=MODULATION_CHOICES, default='qam')
    bandwidth = models.PositiveSmallIntegerField(_('Largura de banda'),
        null=True, help_text='MHz', default=6)
    adapter = models.PositiveSmallIntegerField(null=True)

    def __unicode__(self):
        return str(self.frequency)

    def start(self, adapter_num=None, *args, **kwargs):
        if adapter_num is None:
            self.adapter = self.adapter_num
        else:
            self.adapter = adapter_num
        super(IsdbTuner, self).start(adapter_num)

    def stop(self, *args, **kwargs):
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
            _('There is no PixelView tuner available ' \
              'on server "%s"' % self.server))

    def _get_cmd(self, adapter_num=None):
        cmd = '%s' % settings.DVBLAST_COMMAND
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
                        ('udp', 'UDP'),
                        ('rtp', 'RTP'),
                        )

    interface = models.ForeignKey(NIC, verbose_name=_('Interface de rede'))
    port = models.PositiveSmallIntegerField(_('Porta'), default=10000)
    protocol = models.CharField(_('Protocolo de transporte'), max_length=20,
                                choices=PROTOCOL_CHOICES, default='udp')
    src = generic.GenericRelation(DemuxedService)

    def start(self, *args, **kwargs):
        cmd = self._get_cmd()
        conf = self._get_config()
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
        verbose_name = _('Entrada IP unicast')
        verbose_name_plural = _('Entradas IP unicast')

    def __unicode__(self):
        return '%d [%s]' % (self.port, self.interface)

    def validate_unique(self, exclude=None):
        # unique_together = ('port', 'interface', 'server')
        from django.core.exceptions import ValidationError
        val = UnicastInput.objects.filter(port=self.port,
                                          interface=self.interface,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _('Combinação já existente: %s e %d e %s' % (
                self.server.name, self.port, self.interface))
            raise ValidationError({'__all__': [msg]})

    def has_lock(self):
        "Return True on Multicast and unicast input"
        return True

    def _get_cmd(self):
        cmd = '%s' % settings.DVBLAST_COMMAND
        cmd += ' -D @%s:%d' % (self.interface.ipv4, self.port)
        if self.protocol == 'udp':
            cmd += '/udp'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        return cmd


class MulticastInput(IPInput):
    "Multicast MPEG2TS IP input stream"
    class Meta:
        verbose_name = _('Entrada IP multicast')
        verbose_name_plural = _('Entradas IP multicast')

    ip = models.IPAddressField(_('Endereço IP multicast'))

    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip, self.port, self.interface)

    def validate_unique(self, exclude=None):
        # unique_together = ('ip', 'server')
        from django.core.exceptions import ValidationError
        val = MulticastInput.objects.filter(ip=self.ip,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _('Combinação já existente: %s e %s' % (
                self.server.name, self.ip))
            raise ValidationError({'__all__': [msg]})

    def has_lock(self):
        "Return True on Multicast and unicast input"
        return True

    def _get_cmd(self):
        cmd = '%s' % settings.DVBLAST_COMMAND
        cmd += ' -D @%s:%d' % (self.ip, self.port)
        if self.protocol == 'udp':
            cmd += '/udp'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        return cmd

    def start(self, *args, **kwargs):
        # Create a new rote
        ip = self.ip
        dev = self.server.get_netdev(self.interface.ipv4)
        self.server.create_route(ip, dev)
        super(MulticastInput, self).start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        ip = self.ip
        dev = self.server.get_netdev(self.interface.ipv4)
        self.server.delete_route(ip, dev)
        super(MulticastInput, self).stop(*args, **kwargs)


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
        verbose_name = _('Arquivo de entrada')
        verbose_name_plural = _('Arquivos de entrada')

    filename = models.CharField(
        _('Arquivo de origem'),
        max_length=255,
        blank=True,
        null=True)
    repeat = models.BooleanField(_('Repetir indefinidamente'), default=True)
    src = generic.GenericRelation(UniqueIP)
    nic_src = models.ForeignKey(NIC)

    @property
    def ip(self):
        return self.src.get().ip

    @property
    def port(self):
        return self.src.get().port

    def __unicode__(self):
        if hasattr(self, 'server') is False:
            return self.description
        return '[%s] %s -->' % (self.server, self.description)

    def _get_cmd(self):
        log = logging.getLogger('debug')
        if self.src.count() is not 1:
            raise Exception(
                'A SoftTranscoder must be connected to ONE destination!')
        src = self.src.get()
        log.debug('FileInput._get_cmd() src=%s', src)
        cmd = '%s' % settings.VLC_COMMAND
        cmd += ' -I dummy -v'
        if self.repeat:
            cmd += ' -R'
        #cmd += ' "%s%s"' % (settings.VLC_VIDEOFILES_DIR, self.filename)
        cmd += ' "%s"' % (self.filename)
        cmd += ' --miface %s' % self.nic_src.name
        cmd += ' --sout "#std{access=udp,mux=ts,dst=%s:%d}"' % (
            src.ip, src.port)
        return cmd

    def start(self, *args, **kwargs):
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
        limit_choices_to={"model__in": ("uniqueip",)},
        null=True,
        verbose_name=_('Conexão com device'))
    object_id = models.PositiveIntegerField(null=True)
    sink = generic.GenericForeignKey()

    def stop(self, *args, **kwargs):
        if self.running():
            super(OutputModel, self).stop(*args, **kwargs)
        if kwargs.get('recursive') is True:
            if self.sink.running() is True:
                self.sink.stop(recursive=kwargs.get('recursive'))


class IPOutput(OutputModel, DeviceServer):
    "Generic IP output class"
    class Meta:
        abstract = True

    PROTOCOL_CHOICES = (
                        ('udp', 'UDP'),
                        ('rtp', 'RTP'),
                        )

    interface = models.ForeignKey(NIC,
        verbose_name=_('Interface de rede externa'))
    port = models.PositiveSmallIntegerField(_('Porta'), default=10000)
    protocol = models.CharField(_('Protocolo de transporte'), max_length=20,
        choices=PROTOCOL_CHOICES, default='udp')

    def start(self, *args, **kwargs):
        log = logging.getLogger('debug')
        if self.running() is False:
            # Start multicat
            log_path = '%s%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
            cmd = self._get_cmd()
            log.debug('IPOutput cmd:%s', cmd)
            self.pid = self.server.execute_daemon(cmd,
                log_path=log_path)
            self.status = True
            self.save()
        else:
            log.error('Trying to start %s but is runnig with pid %d', self,
                self.pid)
        if kwargs.get('recursive') is True:
            if self.sink.running() is False:
                self.sink.start(recursive=kwargs.get('recursive'))


class MulticastOutput(IPOutput):
    u"Multicast MPEG2TS IP output stream"
    class Meta:
        verbose_name = _('Saída IP multicast')
        verbose_name_plural = _('Saídas IP multicast')
        ordering = ('ip', )

    ip = models.IPAddressField(_('Endereço IP multicast'), unique=True)
    nic_sink = models.ForeignKey(NIC, related_name='nic_sink',
        verbose_name=_('Interface de rede interna'))

    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip, self.port, self.interface)

    def natural_key(self):
        return {'ip': self.ip, 'port': self.port}

    def _get_cmd(self):
        log = logging.getLogger('debug')
        log.debug('MulticastOutput::_get_cmd() sink=%s nic_sink=%s' % (
            self.sink, self.nic_sink))
        cmd = '%s' % settings.MULTICAT_COMMAND
        cmd += ' -c %s%d.sock' % (settings.MULTICAT_SOCKETS_DIR, self.pk)
        cmd += ' -u @%s:%d/ifaddr=%s' % (
            self.sink.ip, self.sink.port, self.nic_sink.ipv4)
        if self.protocol == 'udp':
            cmd += ' -U'
        cmd += ' %s:%d@%s' % (self.ip, self.port, self.interface.ipv4)
        return cmd


class Storage(DeviceServer):
    'Class to manage recorder storage'

    folder = models.CharField(_('Diretório destino'), max_length=500,
        default=settings.CHANNEL_RECORD_DIR, )
    hdd_ssd = models.BooleanField(_('Disco SSD (Disco Estado Sólido)'),
        default=False)
    peso = models.PositiveIntegerField(
        _('Peso'),
        help_text=_('Prioridade de acesso nas gravações'),
        default=100)
    limit_rec_hd = models.PositiveIntegerField(
        _('Max. Rec. HD'),
        help_text=_('Número máximo de gravações de fluxo HD'),
        default=0)
    limit_rec_sd = models.PositiveIntegerField(
        _('Max. Rec. SD'),
        help_text=_('Número máximo de gravações de fluxo SD'),
        default=0)
    limit_play_hd = models.PositiveIntegerField(
        _('Max. Cli. HD'),
        help_text=_('Número máximo de clientes de fluxo HD'),
        default=0)
    limit_play_sd = models.PositiveIntegerField(
        _('Max. Cli. SD'),
        help_text=_('Número máximo de clientes de fluxo SD'),
        default=0)
    n_recorders = models.PositiveIntegerField(_('Gravações'), default=0)
    n_players = models.PositiveIntegerField(_('Players'), default=0)

    def __unicode__(self):
        return '%s (%s)' % (self.description, self.folder)

    def control_dir(self):
        return '%s/%s/' % (settings.CHANNEL_RECORD_DISKCONTROL_DIR, self.id)

    def _get_cmd(self):
        if settings.CHANNEL_RECORD_DISKCONTROL_VERBOSE:
            verbose = ' -v'
        else:
            verbose = ''
        cmd = '%s%s -l %s' % (settings.CHANNEL_RECORD_DISKCONTROL, verbose,
            self.control_dir())
        return cmd

    def start(self, *args, **kwargs):
        log = logging.getLogger('debug')
        log.info('Iniciando device %s', self)
        # Criando diskctrl dir
        self.server.execute('mkdir -p %s' % self.control_dir())
        log_path = '%sdiskctrl_%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(),
            log_path=log_path)
        if self.pid > 0:
            from django.utils import timezone
            self.start_time = timezone.now()
            self.status = True
            self.n_players = 0
            self.n_recorders = 0
        self.save()

    def stop(self, *args, **kwargs):
        log = logging.getLogger('debug')
        log.info('Stop storage[PID:%s]: %s' % (self.pid, self))
        ## Stop all records
        for r in StreamRecorder.objects.filter(storage=self):
            ## Stop all players for each record
            for p in StreamPlayer.objects.filter(recorder=r):
                if p.pid and p.status:
                    p.stop()
            r.stop(*args, **kwargs)
        if self.running():
            self.n_players = 0
            self.n_recorders = 0
            super(Storage, self).stop(*args, **kwargs)


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
    rotate = models.PositiveIntegerField(_('Tempo em minutos do arquivo'),
        help_text=_('Padrão é 60 min.'), default=60)
    keep_time = models.PositiveIntegerField(_('Horas que permanece gravado'),
        help_text=_('Padrão: 48'), default=48)
    start_time = models.DateTimeField(_('Hora inicial da gravação'),
        null=True, default=None, blank=True)
    channel = models.ForeignKey('tv.Channel', null=True, blank=True)
    nic_sink = models.ForeignKey(NIC,
        verbose_name=_('Interface de rede interna'))
    storage = models.ForeignKey(Storage)
    stream_hd = models.BooleanField(_('Fluxo é HD'),
        help_text=_('Marcar se o fluxo do canal for HD'), default=False)
    ### TODO: hd mecanico e fluxo hd/sd

    class Meta:
        verbose_name = _('Gravador de fluxo')
        verbose_name_plural = _('Gravadores de fluxo')

    def __unicode__(self):
        return 'id:%d rotate:%d, keep:%d, channel:%s' % (
            self.id, self.rotate,
            self.keep_time, self.channel.number)

    def _get_cmd(self):
        import time
        log = logging.getLogger('debug')
        # Create folder to store record files
        self.server.execute('mkdir -p %s/%d' % (self.storage.folder, self.pk))
        # /usr/bin/multicat -c /var/run/multicat/sockets/record_6.sock -u \
        #@239.10.0.1:10000/ifaddr=172.17.0.1 -U -r 97200000000 \
        #-u /iptv/recorder/6

        use_pcrpid = ''
        if settings.CHANNEL_RECORD_USE_PCRPID is True:
            log.info('Record is using pcrpid')
            ## Busca o pid do pcr para o metodo novo de gravação
            demux = self.sink
            print(type(demux))
            while type(demux) is not DemuxedService and demux is not None and \
                hasattr(demux, 'sink'):
                demux = demux.sink
            if type(demux) is DemuxedService:
                time.sleep(3)
                pcrpid = demux.get_pcrpid()
                if pcrpid is None:
                    log.exception('PCRPID cannot be None Demux:%s', demux)
                    raise 'PCRPID cannot be None'
                use_pcrpid = '-p %s ' % pcrpid
                log.info('pcrpid=%s' % pcrpid)

        b = ''
        if self.stream_hd and not self.storage.hdd_ssd:
            b = ' -b'
        cmd = '%s -l %s %s%s -r %d -U -u @%s:%d/ifaddr=%s %s/%d' % (
            settings.CHANNEL_RECORD_COMMAND,
            self.storage.control_dir(),
            b,
            use_pcrpid,
            (self.rotate * 60 * 27000000),
            self.sink.ip,
            self.sink.port,
            self.nic_sink.ipv4,
            self.storage.folder,
            self.pk,
            )
        return cmd

    def start(self, *args, **kwargs):
        log = logging.getLogger('debug')
        log.info('Starting new record: %s' % self)
        # Force start sink on start record
        if self.sink.running() is False:
            self.sink.start(recursive=kwargs.get('recursive'))
        if not self.storage.running():
            self.storage.start()
        # Start multicat
        log_path = '%srecorder_%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(),
            log_path=log_path)
        if self.pid > 0:
            from django.utils import timezone
            self.start_time = timezone.now()
            self.status = True
            self.storage.n_recorders += 1
            self.storage.save()
        self.save()
        self.install_cron()

    def stop(self, *args, **kwargs):
        log = logging.getLogger('debug')
        log.info('Stop record[PID:%s]: %s' % (self.pid, self))
        if self.running():
            super(StreamRecorder, self).stop(*args, **kwargs)
            ## Verifica se existe algum gravador usando o mesmo storage
            ## Se não existe para o storage
            # StreamRecorder.objects.filter(storage=self.storage, status=True)
            self.storage.n_recorders -= 1
            self.storage.save()
        if kwargs.get('recursive') is True:
            if self.sink.running() is True:
                self.sink.stop(recursive=kwargs.get('recursive'))
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
        elements = (self.keep_time / (self.rotate / 60)) + 1
        cmd = '*/30 * * * * %s %s/%d/ %d' % (
            settings.CHANNEL_RECORD_CLEAN_COMMAND,
            self.storage.folder,
            self.id,
            elements)
        return cmd

    def install_cron(self):
        'Reinstall crontab for current server\
        (for now full install all recorders)'
        from tempfile import NamedTemporaryFile
        from django.utils import timezone
        log = logging.getLogger('debug')
        log.info('Installing new cron on %s' % self.server)
        # Get all running recorders on current recorder server
        recorders = StreamRecorder.objects.filter(
            server=self.server, status=True)
        #if len(recorders) == 0:
        #    return
        tmpfile = NamedTemporaryFile()
        start_time = timezone.now()
        log.debug('CronTime:%s', start_time)
        cron = '# New cronfile: %s \n\n' % start_time
        remote_tmpfile = "".join(self.server.execute('/bin/mktemp')).strip()
        for rec in recorders:
            cron += '# recorder = %s\n' % rec.pk
            line = rec.get_cron_line()
            log.info('    cronline:%s' % line)
            cron += line + '\n\n'
        tmpfile.file.write(cron)
        tmpfile.file.flush()
        if self.server.offline_mode is False:
            self.server.put(tmpfile.name, remote_tmpfile)
        self.server.execute('/usr/bin/crontab %s ' % remote_tmpfile)
        tmpfile.close()


#@receiver(pre_save, sender=StreamRecorder)
#def StreamRecorder_pre_save(sender, instance, **kwargs):
#    "Filling dependent fields from Channel"
#    if instance.channel is not None:
#        channel = instance.channel
#        content_type_id = channel.source.content_type_id
#        instance.content_type_id = content_type_id


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
    stb_ip = models.IPAddressField(_('IP destino'), db_index=True,
        unique=True)
    stb_port = models.PositiveSmallIntegerField(_('Porta destino'),
        help_text=_('Padrão: %s' % (settings.CHANNEL_PLAY_PORT)),
        default=settings.CHANNEL_PLAY_PORT)
    # Socket de controle do aplicativo no servidor
    control_socket = models.CharField(_('Socket de controle (auto)'),
        max_length=500)
    time_shift = models.PositiveIntegerField(_('Segundos'), default=0)
    stb = models.ForeignKey('client.SetTopBox', null=True, blank=True)

    class Meta:
        verbose_name = _('Reprodutor de fluxo gravado')
        verbose_name_plural = _('Reprodutores de fluxo gravado')

    def __unicode__(self):
        return 'StreamPlayer: STB="%s:%s" ch="%s"' % (self.stb_ip,
            self.stb_port,
            self.recorder.channel.number)

    def play(self, time_shift=0):
        ur"""
        Localizar um servidor de gravação que tenha o canal gravado no horário
        solicitado.
        Caso esteja rodando um vídeo anterior, interromper este antes de
        executar o novo.
        """
        log = logging.getLogger('tvod')
        log.info('PLAY:%s', self)
        if self.status and self.pid:
            self.stop()
        return self.start(time_shift=time_shift)

    def pause(self, time_shift=0):
        ur"""
        Abre o socket da reprodução atual chamando o multicatctl e envia o
        comando pause para o soket específico
        multicatctl -c /xxx/multicat_yy.socket pause
        """
        from django.core.cache import get_cache
        cache = get_cache('default')
        log = logging.getLogger('tvod')
        log.info('PAUSE:%s', self)
        if self.status and self.pid:
            key = 'StreamPlayer[%d].status' % self.id
            status = cache.get(key)
            if status == 'paused':
                cmd = '%s -r %s play' % (
                    settings.MULTICATCTL_COMMAND,
                    self.control_socket,
                    )
                new_status = 'play'
            else:
                cmd = '%s -r %s pause' % (
                    settings.MULTICATCTL_COMMAND,
                    self.control_socket,
                    )
                new_status = 'paused'
            cache.set(key, new_status)
            log.info('%s=%s', key, new_status)
            self.server.execute_daemon(cmd)
            self.status = True
            self.time_shift = time_shift
            self.save()
        else:
            log.error('Player not runnig:%s', self)
            new_status = 'not running'
        return new_status

    def _get_cmd(self, time_shift=0):
        self.control_socket = '%sclient_%d.sock' % (
            settings.MULTICAT_SOCKETS_DIR,
            self.pk)
        b = ''
        if self.recorder.stream_hd and not self.recorder.storage.hdd_ssd:
            b = ' -b'
        cmd = '%s%s -l %s -c %s -r %s -k -%s -U %s/%d %s:%d' % (
            settings.CHANNEL_RECORD_PLAY_COMMAND,
            b,
            self.recorder.storage.control_dir(),
            self.control_socket,
            (self.recorder.rotate * 60 * 27000000),
            (time_shift * 27000000),
            self.recorder.storage.folder,
            self.recorder.pk,
            self.stb_ip,
            self.stb_port
            )
        return cmd

    def start(self, recursive=False, time_shift=0):
        # Start multicat
        log_path = '%splayer_%d' % (settings.MULTICAT_LOGS_DIR, self.id)
        cmd = self._get_cmd(time_shift=time_shift)
        self.pid = self.server.execute_daemon(cmd, log_path=log_path)
        self.status = True
        self.time_shift = time_shift
        storage = self.recorder.storage
        storage.n_players += 1
        storage.save()
        self.save()

    def stop(self, *args, **kwargs):
        log = logging.getLogger('tvod')
        log.info('STOP:%s', self)
        super(StreamPlayer, self).stop(*args, **kwargs)
        storage = self.recorder.storage
        if storage.n_players > 0:
            storage.n_players -= 1
            storage.save()
        self.server.rm_file(self.control_socket)


class SoftTranscoder(DeviceServer):
    "A software transcoder device"

    AUDIO_CODECS_LIST = (
        ('mp2', 'MP2'),
        ('aac', 'AAC'),
        ('ac3', 'AC3'),
    )

    nic_sink = models.ForeignKey(NIC, related_name='soft_transcoder_nic_sink')
    nic_src = models.ForeignKey(NIC, related_name='soft_transcoder_nic_src')
    content_type = models.ForeignKey(ContentType,
        limit_choices_to={"model__in": ("uniqueip",)},
        null=True,
        verbose_name=_('Conexão com device'))
    object_id = models.PositiveIntegerField(null=True)
    sink = generic.GenericForeignKey()
    src = generic.GenericRelation(UniqueIP)
    # Audio transcoder
    transcode_audio = models.BooleanField('Transcodificar áudio', default=False)
    audio_codec = models.CharField('Áudio codec', max_length=100,
        choices=AUDIO_CODECS_LIST, null=True, blank=True)
    # Gain control filter
    apply_gain = models.BooleanField('Aplicar ganho', default=False)
    gain_value = models.FloatField('Ganho multiplicador',
        help_text='Increase or decrease the gain (default 1.0)',
        default=1.0, null=True, blank=True)  # --gain-value
    # Offset control filter
    apply_offset = models.BooleanField('Aplicar offset', default=False)
    offset_value = models.IntegerField('Valor offset',
        help_text='Increase or decrease offset (default 0)',
        default=0, null=True, blank=True)  # --offset-value
    restart = False

    class Meta:
        verbose_name = _('Transcodificador em Software')
        verbose_name_plural = _('Transcodificadores em Software')

    def __unicode__(self):
        return 'Transcoder %s - %s' % (self.audio_codec, self.description)

    def _get_gain_filter_options(self):
        return '-af volume=volume=%.2f' % self.gain_value

    def _get_offset_filter_options(self):
        return '-af volume=volume=%.2fdB' % self.offset_value
 
    def _get_cmd(self):
        import re
        cmd = '%s -i ' % settings.FFMPEG_COMMAND
        if re.match(r'^2[23]\d\.', self.sink.ip):  # is multicast
            input_addr = '"udp://%s:%d?localaddr=%s"' % (
                self.sink.ip, self.sink.port, self.nic_sink.ipv4)
        else:
            input_addr = '"udp://%s:%d"' % (self.sink.ip, self.sink.port)
        if self.src.count() is not 1:
            raise Exception(
                'A SoftTranscoder must be connected to ONE destination!')
        src = self.src.get()
        output = '"udp://%s:%d?localaddr=%s&pkt_size=1316"' % (
            src.ip, src.port, self.nic_src.ipv4
        )
        if self.transcode_audio is True:
            afilters = []
            if self.apply_gain:
                afilters.append(self._get_gain_filter_options())
            if self.apply_offset:
                afilters.append(self._get_offset_filter_options())
            cmd += '%s -vcodec copy -acodec %s %s -f mpegts %s' \
            % (
                input_addr, self.audio_codec,
                ' '.join(afilters), output
            )
        else:
            cmd += '%s -vcodec copy -acodec copy -f mpegts %s' % (input_addr, output)
        return cmd

    def start(self, *args, **kwargs):
        log_path = '%s%d' % (settings.FFMPEG_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(),
            log_path=log_path)
        if self.pid > 0:
            self.status = True
        self.save()
        if kwargs.get('recursive') is True:
            if self.sink.running() is False:
                self.sink.start(recursive=kwargs.get('recursive'))

    def stop(self, *args, **kwargs):
        self.server.execute('/bin/kill %d' % (self.pid))
        super(SoftTranscoder, self).stop(*args, **kwargs)
        if kwargs.get('recursive') is True:
            if self.sink.running() is True:
                self.sink.stop(recursive=kwargs.get('recursive'))

    def clean(self):
        from django.core.exceptions import ValidationError
        # You need to specify a codec if transcoding is enabled
        if self.transcode_audio is True and self.audio_codec is None:
            raise ValidationError(
                _('Especifique o codec para transcodificação.'))
        # Filters will only be applied if transcoding is enabled
        if self.transcode_audio is False and (
            self.apply_gain is True or \
            self.apply_offset is True):
            raise ValidationError(
                _('Os filtros só serão aplicados se a'
                ' transcodificação estiver habilitada.'))


@receiver(post_save, sender=SoftTranscoder)
def SoftTranscoder_post_save(sender, instance, **kwargs):
    log = logging.getLogger('debug')
    log.debug('SoftTranscoder::post_save')
    if instance.restart is True:
        return
    if instance.running() is True:
        instance.restart = True
        instance.stop()
        instance.start()
        instance.restart = False


class RealTimeEncript(models.Model):
    u"""RealTime to manage stream flow"""



