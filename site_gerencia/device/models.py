#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils.functional import lazy
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType, ContentTypeManager


class Server(models.Model):
    """
    Servidor e caracteristicas de conexão.
    """

    class Meta:
        verbose_name = _(u'Servidor de Recursos')
        verbose_name_plural = _(u'Servidores de Recursos')

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
    
    class ExecutionFailure(Exception):
        def __init__(self, value):
            self.parameter = value
        def __str__(self):
            return repr(self.parameter)
    
    class InvalidOperation(Exception):
        pass
    
    def __unicode__(self):
        return '%s' % (self.name)

    def switch_link(self):
        url = reverse('device.views.server_status', kwargs={'pk': self.id})
        return '<a href="%s" id="server_id_%s" >Atualizar</a>' % (url, self.id)

    switch_link.allow_tags = True

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
            raise Server.InvalidOperation("Shouldn't connect when offline mode is set")
        s = None
        try:
            s = ssh.Connection(host=self.host,
                port=self.ssh_port,
                username=self.username,
                password=self.password,
                private_key=self.rsakey)
            self.status = True
            self.msg = 'OK'
        except ValueError:
            self.status = False
            self.msg = ValueError
        except Exception as ex:
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
        ret = {}
        try:
            ret = s.execute(command)
            w = ret['output']
        except Exception as ex:
            self.msg = ex
            w = 'ERROR'
        if not persist and self.status:
            s.close()
        self.save()
        if ret.has_key('exit_code') and ret['exit_code'] is not 0:
                raise Server.ExecutionFailure(
                    'Command "%s" returned status "%d" on server "%s": "%s"' %
                    (command, ret['exit_code'], self, "".join(ret['output'])))
        return w

    def execute_daemon(self, command):
        "Excuta o processo em background (daemon)"
        try:
            s = self.connect()
            self.msg = 'OK'
        except Exception as ex:
            self.msg = ex
            self.status = False
            raise ex
        pid = s.execute_daemon(command)
        s.close()
        self.save()
        return int(pid)

    def process_alive(self, pid):
        "Verifica se o processo está em execução no servidor"
        for p in self.list_process():
            if p['pid'] == pid:
                return True
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
        s = self.connect()
        resp = s.execute('/bin/kill %d' % pid)
        s.close()
        return resp

    def auto_create_nic(self):
        """
        Auto create NIC (Network interfaces)
        """
        nics = []
        for iface in self._list_interfaces():
            nics.append(
                NIC.objects.get_or_create(
                    name=iface['dev'],
                    ipv4=iface['ip'],
                    server=self))
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
        self.execute('/usr/bin/sudo /sbin/route add -host %s dev %s' % (ip, dev))

    def delete_route(self, ip, dev):
        "Delete a route on the server"
        self.execute('/usr/bin/sudo /sbin/route del -host %s dev %s' % (ip, dev))
    
    def list_routes(self):
        resp = []
        routes = self.execute('/sbin/route -n')
        for route in routes[2:]:
            r = route.split()
            resp.append((r[0], r[-1]))
        
        return resp

    def list_dir(self, directory='/'):
        "Lista o diretório no servidor retornando uma lista do conteúdo"
        ret = self.execute('/bin/ls %s' % directory)
        return map(lambda x: x.strip('\n'), ret)
    
    def cat_file(self, path):
        "Return the contents of a File given his path"
        ret = self.execute('/bin/cat %s' % path)
        content = u''.join(ret)
        return content.strip()

class NIC(models.Model):
    'Classe de manipulação da interface de rede e referencia do servidor'
    name = models.CharField(_(u'Interface de rede'), max_length=50)
    server = models.ForeignKey(Server)
    ipv4 = models.IPAddressField(_(u'Endereço ip v4 atual'))

    def __unicode__(self):
        return u'%s->%s(%s)' % (self.server, self.name, self.ipv4)

class UniqueIP(models.Model):
    """
    Classe de endereço ip externo (na rede dos clientes)
    """
    class Meta:
        verbose_name = _(u'Endereço de fluxo externo')
        verbose_name_plural = _(u'Endereços de fluxo externo')
    ip = models.IPAddressField(_(u'Endereço IP'),
        unique=True,
        null=True
        )
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    nic = models.ForeignKey(NIC)
    sequential = models.PositiveSmallIntegerField(
        _(u'Valor auxiliar para gerar o IP único'),
        default=2)
    
    ## Para o relacionamento genérico de origem
    sink = generic.GenericForeignKey()
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return '[%d] %s:%d' % (self.sequential, self.ip, self.port)
    
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
        self.ip = self._gen_ip()
        super(UniqueIP, self).save(*args, **kwargs)

    def _gen_ip(self):
        ip = settings.EXTERNAL_IP_MASK % (
            self.sequential / 256,
            self.sequential % 256)
        return ip

    def start(self):
        self.sink.start()


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

    def _type(self):
        return _(u'undefined')

    def start(self):
        raise Exception('Must be overridden')

    def stop(self):
        """Interrompe processo no servidor"""
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

class Dvblast(DeviceServer):
    "DEPRECATED: Não utilizado mais???"
    class Meta:
        verbose_name = _(u'DVBlast')
        verbose_name_plural = _(u'DVBlast')

    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    is_rtp = models.BooleanField(_(u'RTP'),default=False)

    def __unicode__(self):
        return '%s (%s:%s)' %(self.name,self.ip,self.port)

    def status(self):
        from lib.player import Player
        p = Player()
        if p.is_playing(self) is True:
            url = reverse('device.views.stop',kwargs={'streamid':self.id})
            return '<a href="%s" id="stream_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('device.views.play',kwargs={'streamid':self.id})
        return '<a href="%s" id="stream_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
        #return '%s'%self.id
    status.allow_tags = True

    def play(self):
        'Inicia o fluxo (inicia o processo do multicat)'
        from lib.player import Player
        p = Player()
        pid = p.play_stream(self)
        self.pid = pid
        self.save()


class Channel(models.Model):
    class Meta:
        verbose_name = _(u'Canal')
        verbose_name_plural = _(u'Canais')
    
    def __unicode__(self):
        return '%s -> %s' % (self.input, self.output)
    
    def play(self):
        pass
    
    # Input
    input_limit = models.Q(app_label = 'device', model = 'DemuxedInput') | \
                models.Q(app_label = 'device', model = 'DvbTuner') | \
                models.Q(app_label = 'device', model = 'IsdbTuner') | \
                models.Q(app_label = 'device', model = 'UnicastInput') | \
                models.Q(app_label = 'device', model = 'MulticastInput')
    input_content_type = models.ForeignKey(ContentType, limit_choices_to = input_limit)
    input_object_id = models.PositiveIntegerField()
    input = generic.GenericForeignKey('input_content_type', 'input_object_id')
    # Output
    output = models.ForeignKey('MulticastOutput', null=True, blank=True)
    # Recorder
    recorder = models.ForeignKey('StreamRecorder', null=True, blank=True)

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
    lnb_type = models.CharField(_(u'Tipo de LNB'), max_length=200, choices=LNBS)
    
    def __unicode__(self):
        return str(self.satellite)

class DemuxedService(models.Model):
    class Meta:
        verbose_name = _(u'Entrada demultiplexada')
        verbose_name_plural = _(u'Entradas demultiplexadas')
    
    def __unicode__(self):
        return ('[%d] %s - %s') % (self.sid, self.provider, self.service_desc)
    
    def start(self):
        self.sink.start()
    
    sid = models.PositiveSmallIntegerField(_(u'Programa'))
    provider = models.CharField(_(u'Provedor'), max_length=200, null=True, blank=True)
    service_desc = models.CharField(_(u'Serviço'), max_length=200, null=True, blank=True)
    src = generic.GenericRelation(UniqueIP)
    # Sink (connect to a Tuner or IP input)
    content_type = models.ForeignKey(ContentType,
         limit_choices_to = {"model__in": ("DvbTuner", "IsdbTuner", 
                                           "UnicastInput", "MulticastInput")},
         null=True)
    object_id = models.PositiveIntegerField(null=True)
    sink = generic.GenericForeignKey()

class InputModel(models.Model):
    "Each model of input type should inherit this"
    class Meta:
        abstract = True
    
    def _get_config(self):
        # Fill config file
        conf = u''
        for service in self.src.all():
            if service.src.count() > 0:
                sid = service.sid
                ip = service.src.all()[0].ip
                port = service.src.all()[0].port
                # Assume internal IPs always work with raw UDP
                conf += "%s:%d/udp 1 %d\n" % (ip, port, sid)
        
        return conf
    
    def _create_folders(self):
        "Creates all the folders dvblast needs"
        self.server.execute('mkdir -p %s' % settings.DVBLAST_CONFS_DIR, persist=True)
        self.server.execute('mkdir -p %s' % settings.DVBLAST_SOCKETS_DIR, persist=True)
        self.server.execute('mkdir -p %s' % settings.DVBLAST_LOGS_DIR)

class DigitalTuner(InputModel, DeviceServer):
    class Meta:
        abstract = True
    
    def start(self):
        "Starts a dvblast instance based on the current model's configuration"
        cmd = self._get_cmd()
        conf = self._get_config()
        # Create the necessary folders
        self._create_folders()
        # Write the config file to disk
        self.server.execute('echo "%s" > %s%d.conf' % (conf, 
                                settings.DVBLAST_CONFS_DIR, self.pk), persist=True)
        # Start dvblast process
        log_path = '%s%d' % (settings.DVBLAST_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(cmd, log_path=log_path)
        self.save()
    
    frequency = models.PositiveIntegerField(_(u'Frequência'), help_text=u'MHz')
    src = generic.GenericRelation(DemuxedService)

class DvbTuner(DigitalTuner):
    class Meta:
        verbose_name = _(u'Sintonizador DVB-S/S2')
        verbose_name_plural = _(u'Sintonizadores DVB-S/S2')
    
    def __unicode__(self):
        return '%s - %d %s %d' % (self.antenna,self.frequency,self.polarization,self.symbol_rate)
    
    @property
    def adapter_num(self):
        import re
        files = self.server.execute('/bin/find /dev/dvb/ -name adapter*.mac -type f', persist=True)
        for file in files:
            contents = self.server.cat_file(file)
            if contents == self.adapter:
                m = re.match(r'/dev/dvb/adapter(\d+)\.mac', file)
                return m.group(1)
        # TODO: Should throw exception
    
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
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        
        return cmd
    
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
    
    symbol_rate = models.PositiveIntegerField(_(u'Taxa de símbolos'), help_text=u'Msym/s')
    modulation = models.CharField(_(u'Modulação'), max_length=200, choices=MODULATION_CHOICES)
    polarization = models.CharField(_(u'Polarização'), max_length=200, choices=POLARIZATION_CHOICES)
    fec = models.CharField(_(u'FEC'), max_length=200, choices=FEC_CHOICES, default=u'999')
    adapter = models.CharField(_(u'Adaptador'), max_length=200)
    antenna = models.ForeignKey(Antenna, verbose_name=_(u'Antena'))

class IsdbTuner(DigitalTuner):
    class Meta:
        verbose_name = _(u'Sintonizador ISDB-Tb')
        verbose_name_plural = _(u'Sintonizadores ISDB-Tb')
    
    def __unicode__(self):
        return str(self.frequency)
    
    @property
    def adapter_num(self):
        """TODO: Improve implementation. This one will cause a 
        race condition if two instances hit start simultaneously"""
        import re
        # Get adapters list
        files = self.server.execute('/bin/find /dev/dvb/ -name adapter*.mac -type f', persist=True)
        adapters = []
        for file in files:
            contents = self.server.cat_file(file)
            if contents == 'PixelView':
                m = re.match(r'/dev/dvb/adapter(\d+)\.mac', file)
                adapters.append(m.group(1))
        # Now exclude all used adapters from list
        ps = self.server.execute('ps aux | grep %s' % settings.DVBLAST_COMMAND)
        for line in ps:
            m = re.match(r'-a (\d+)', line)
            if m:
                adapters.remove(m.group(1))
        # At least one should be left
        if len(adapters) > 0:
            return adapters[0] # Return the first free one
        else:
            raise Exception("Tried to start a IsdbTuner but there's no device available")
    
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
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
        
        return cmd
    
    MODULATION_CHOICES = (
                          (u'qam', u'QAM'),
                          )
    
    modulation = models.CharField(_(u'Modulação'), max_length=200, choices=MODULATION_CHOICES, default=u'qam')
    bandwidth = models.PositiveSmallIntegerField(_(u'Largura de banda'), null=True, help_text=u'MHz', default=6)

class IPInput(InputModel, DeviceServer):
    "Generic IP input class"
    class Meta:
        abstract = True
    
    def start(self):
        cmd = self._get_cmd()
        conf = self._get_config()
        # Create the necessary folders
        self._create_folders()
        # Write the config file to disk
        self.server.execute('echo "%s" > %s%d.conf' % (conf, 
                                settings.DVBLAST_CONFS_DIR, self.pk), persist=True)
        # Start dvblast process
        log_path = '%s%d' % (settings.DVBLAST_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(cmd, log_path=log_path)
        self.save()
    
    PROTOCOL_CHOICES = (
                        (u'udp', u'UDP'),
                        (u'rtp', u'RTP'),
                        )
    
    interface = models.ForeignKey(NIC, verbose_name=_(u'Interface de rede'))
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    protocol = models.CharField(_(u'Protocolo de transporte'), max_length=20,
                                choices=PROTOCOL_CHOICES, default=u'udp')
    src = generic.GenericRelation(DemuxedService)

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
            msg = _(u'Combinação já existente: %s e %d e %s' % (self.server.name, self.port, self.interface))
            raise ValidationError({'__all__' : [msg]})
    
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
    
    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip, self.port, self.interface)
    
    def validate_unique(self, exclude=None):
        # unique_together = ('ip', 'server')
        from django.core.exceptions import ValidationError
        val = MulticastInput.objects.filter(ip=self.ip,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _(u'Combinação já existente: %s e %s' % (self.server.name, self.ip))
            raise ValidationError({'__all__' : [msg]})
    
    def _get_cmd(self):
        cmd = u'%s' % settings.DVBLAST_COMMAND
        cmd += ' -D @%s:%d' % (self.ip, self.port)
        if self.protocol == 'udp':
            cmd += '/udp'
        cmd += ' -c %s%d.conf' % (settings.DVBLAST_CONFS_DIR, self.pk)
        cmd += ' -r %s%d.sock' % (settings.DVBLAST_SOCKETS_DIR, self.pk)
            
        return cmd
    
    ip = models.IPAddressField(_(u'Endereço IP multicast'))

@receiver(pre_save, sender=MulticastInput)
def MulticastInput_pre_save(sender, instance, **kwargs):
    "Signal to create the route"
    server = instance.server
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
    
    file_list = None
    
    def get_list_dir(self):
        if self.server_id is None:
            return []
        if self.file_list is None and self.server.status is True:
            self.file_list = []
            d = self.server.list_dir(settings.VIDEO_LOOP_DIR)
            for f in d:
                self.file_list.append((f, f))
        if self.file_list is None:
            return []
        return self.file_list
    
    def __init__(self, *args, **kwargs):
        super(FileInput, self).__init__(*args, **kwargs)
        if self.server_id is not None:
            self._meta.get_field_by_name('filename')[0]._choices = lazy(
                self.get_list_dir, list)()
    
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
        cmd += ' "%s%s"' % (settings.VLC_VIDEOFILES_DIR, self.filename)
        cmd += ' --sout "#std{access=udp,mux=ts,dst=%s:%d}"' % (
                                        ip.ip, ip.port)
        
        return cmd
    
    def start(self):
        """Inicia processo do VLC"""
        self.pid = self.server.execute_daemon(self._get_cmd())
        self.status = True
        self.save()
        return self.status
    
    def switch_link(self):
        if self.sink is None or self.server_id is None:
            return 'Desconfigurado'
        if self.running():
            url = reverse('device.views.vlc_stop',kwargs={'pk': self.id})
            return '<a href="%s" id="vlc_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' % (url,self.id)
        url = reverse('device.views.vlc_start',kwargs={'pk': self.id})
        return '<a href="%s" id="vlc_id_%s" style="color:red;" >Parado</a>' % (url,self.id)
    switch_link.allow_tags = True

class OutputModel(models.Model):
    "Each model of output type should inherit this"
    class Meta:
        abstract = True
    
    def _create_folders(self):
        "Creates all the folders multicat needs"
        self.server.execute('mkdir -p %s' % settings.MULTICAT_SOCKETS_DIR, persist=True)
        self.server.execute('mkdir -p %s%d' % (settings.MULTICAT_RECORDINGS_DIR, self.pk), persist=True)
        self.server.execute('mkdir -p %s' % settings.MULTICAT_LOGS_DIR, persist=True)
    
    content_type = models.ForeignKey(ContentType,
                            limit_choices_to = {"model__in": ("UniqueIP",)},
                            null=True)
    object_id = models.PositiveIntegerField(null=True)
    sink = generic.GenericForeignKey()

class IPOutput(OutputModel, DeviceServer):
    "Generic IP output class"
    class Meta:
        abstract = True
    
    def start(self):
        # Create the necessary folders
        self._create_folders()
        # Start multicat
        log_path = '%s%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(), log_path=log_path)
        self.save()
    
    PROTOCOL_CHOICES = (
                        (u'udp', u'UDP'),
                        (u'rtp', u'RTP'),
                        )
    
    interface = models.ForeignKey(NIC, verbose_name=_(u'Interface de rede'))
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    protocol = models.CharField(_(u'Protocolo de transporte'), max_length=20,
                                choices=PROTOCOL_CHOICES, default=u'udp')

class MulticastOutput(IPOutput):
    "Multicast MPEG2TS IP output stream"
    class Meta:
        verbose_name = _(u'Saída IP multicast')
        verbose_name_plural = _(u'Saídas IP multicast')
    
    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip_out, self.port, self.interface)
    
    def validate_unique(self, exclude=None):
        # unique_together = ('ip', 'server')
        from django.core.exceptions import ValidationError
        val = MulticastOutput.objects.filter(ip=self.ip,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _(u'Combinação já existente: %s e %s' % (self.server.name, self.ip))
            raise ValidationError({'__all__' : [msg]})
    
    def _get_cmd(self):
        cmd = u'%s' % settings.MULTICAT_COMMAND
        cmd += ' -c %s%d.sock' % (settings.MULTICAT_SOCKETS_DIR, self.pk)
        cmd += ' -u @%s:%d' % (self.sink.ip, self.sink.port)
        if self.protocol == 'udp':
            cmd += ' -U'
        cmd += ' %s:%d' % (self.ip_out, self.port)
        
        return cmd
    
    ip_out = models.IPAddressField(_(u'Endereço IP multicast'))

class StreamRecorder(OutputModel, DeviceServer):
    class Meta:
        verbose_name = _(u'Gravador de fluxo')
        verbose_name_plural = _(u'Gravadores de fluxo')
        
    def _get_cmd(self):
        cmd = u'%s' % settings.MULTICAT_COMMAND
        cmd += ' -r %d' % (self.rotate * 60 * 27000000) # Convert to timestamps
        cmd += ' -c %s%d.sock' % (settings.MULTICAT_SOCKETS_DIR, self.pk)
        cmd += ' -u @%s:%d' % (self.sink.ip, self.sink.port)
        cmd += ' %s%d' % (settings.MULTICAT_RECORDINGS_DIR, self.pk)
        
        return cmd
    
    def start(self):
        # Create the necessary folders
        self._create_folders()
        # Start multicat
        log_path = '%s%d' % (settings.MULTICAT_LOGS_DIR, self.pk)
        self.pid = self.server.execute_daemon(self._get_cmd(), log_path=log_path)
        self.save()
    
    rotate = models.PositiveIntegerField()
    folder = models.CharField(max_length=500)
