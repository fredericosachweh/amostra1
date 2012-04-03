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
            self.msg = 'Can not connect:' + ex
        try:
            w = s.execute(command)
        except Exception as ex:
            self.msg = ex
            w = 'ERROR'
        if not persist and self.status:
            s.close()
        self.save()
        return w

    def execute_daemon(self, command):
        "Excuta o processo em background (daemon)"
        try:
            s = self.connect()
            self.msg = 'OK'
        except Exception as ex:
            self.msg = ex
            self.status = False
        pid = s.execute_daemon(command)
        s.close()
        self.save()
        return pid

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
        return NIC.objects.get(server=self, ipv4=ip)

    def create_route(self, ip, dev):
        "Create a new route on the server"
        self.execute('/sbin/route add -host %s dev %s' % (ip, dev))

    def delete_route(self, ip, dev):
        "Delete a route on the server"
        self.execute('/sbin/route del -host %s dev %s' % (ip, dev))

    def list_dir(self, directory='/'):
        "Lista o diretório no servidor retornando uma lista do conteúdo"
        ret = self.execute('/bin/ls %s' % directory)
        return map(lambda x: x.strip('\n'), ret)


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
    sink = generic.GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return '[%d] %s:%d' % (self.sequential, self.ip, self.port)

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
        super(UniqueIP, self).save(*args, **kwargs)

    def _gen_ip(self):
        ip = settings.EXTERNAL_IP_MASK % (
            self.sequential / 256,
            self.sequential % 256)
        return ip


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
        raise Exception('Must be overload')

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


class Vlc(DeviceServer):
    """
    VLC streaming device.
    file -> vlc -> output -> ip
    """
    class Meta:
        verbose_name = _(u'Vídeo em loop')
        verbose_name_plural = _(u'Vídeos em loop')

    sink = models.CharField(
        _(u'Arquivo de origem'),
        max_length=255,
        blank=True,
        null=True)
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
        super(Vlc, self).__init__(*args, **kwargs)
        if self.server_id is not None:
            self._meta.get_field_by_name('sink')[0]._choices = lazy(
                self.get_list_dir, list)()
    
    def __unicode__(self):
        if hasattr(self, 'server') is False:
            return self.description
        return '[%s] %s -->' % (self.server, self.description)

    def start(self):
        """Inicia processo do VLC"""
        ip = self.src.get()
        s = self.sink.replace(' ','\ ').replace("'","\\'").replace('(','\(').replace(')','\)')
        c = '/usr/bin/cvlc -I dummy -v -R %s ' \
            '--sout "#std{access=udp,mux=ts,dst=%s:%d}"' % (
            s,
            ip.ip,
            ip.port)
        c = self.server.execute_daemon(c)
        self.status = True
        self.pid = c
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

class DemuxedInput(models.Model):
    class Meta:
        verbose_name = _(u'Entrada demultiplexada')
        verbose_name_plural = _(u'Entradas demultiplexadas')
    
    def __unicode__(self):
        return ('%s - %s') % (self.provider, self.service)
    
    sid = models.PositiveSmallIntegerField(_(u'Programa'))
    provider = models.CharField(_(u'Provedor'), max_length=200, null=True, blank=True)
    service = models.CharField(_(u'Serviço'), max_length=200, null=True, blank=True)

class Demuxer(DeviceServer):
    class Meta:
        verbose_name = _(u'Demultiplexador MPEG2TS')
        verbose_name_plural = _(u'Demultiplexadores MPEG2TS')
    
    demuxed_inputs = models.ManyToManyField(DemuxedInput, null=True, blank=True)

class DigitalTuner(DeviceServer):
    class Meta:
        abstract = True
    
    frequency = models.PositiveIntegerField(_(u'Frequência'), help_text=u'MHz')


class DvbTuner(DigitalTuner):
    class Meta:
        verbose_name = _(u'Sintonizador DVB-S/S2')
        verbose_name_plural = _(u'Sintonizadores DVB-S/S2')
    
    def __unicode__(self):
        return '%s - %d %s %d' % (self.antenna,self.frequency,self.polarization,self.symbol_rate)
    
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
    
    symbol_rate = models.PositiveIntegerField(_(u'Taxa de símbolos'), help_text=u'Msym/s')
    modulation = models.CharField(_(u'Modulação'), max_length=200, choices=MODULATION_CHOICES)
    polarization = models.CharField(_(u'Polarização'), max_length=200, choices=POLARIZATION_CHOICES)
    adapter = models.CharField(_(u'Adaptador'), max_length=200)
    antenna = models.ForeignKey(Antenna, verbose_name=_(u'Antena'))
    # /usr/bin/dvblast -a %s -m %s %(adapter.get_order(),psk_s)


class IsdbTuner(DigitalTuner):
    class Meta:
        verbose_name = _(u'Sintonizador ISDB-Tb')
        verbose_name_plural = _(u'Sintonizadores ISDB-Tb')
    
    def __unicode__(self):
        return str(self.frequency)
    
    MODULATION_CHOICES = (
                          (u'QAM', u'QAM'),
                          )
    
    modulation = models.CharField(_(u'Modulação'), max_length=200, choices=MODULATION_CHOICES, default=u'QAM')
    bandwidth = models.PositiveSmallIntegerField(_(u'Largura de banda'), null=True, help_text=u'MHz', default=6)


class IPInput(DeviceServer):
    "Generic IP input class"
    class Meta:
        abstract = True
    
    PROTOCOL_CHOICES = (
                        (u'udp', u'UDP'),
                        (u'rtp', u'RTP'),
                        )
    
    interface = models.IPAddressField(_(u'Interface de rede'))
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    protocol = models.CharField(_(u'Protocolo de transporte'), max_length=20,
                                choices=PROTOCOL_CHOICES, default=u'udp')

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
    
    ip = models.IPAddressField(_(u'Endereço IP multicast'))

@receiver(pre_save, sender=MulticastInput)
def MulticastInput_pre_save(sender, instance, **kwargs):
    "Signal to create the route"
    server = instance.server
    # If it already exists, delete 
    try:
        obj = MulticastInput.objects.get(pk=instance.pk)
        ip = obj.ip
        dev = server.get_netdev(obj.interface)
        server.delete_route(ip, dev)
    except MulticastInput.DoesNotExist:
        pass
    
    # Create a new rote
    ip = instance.ip
    dev = server.get_netdev(instance.interface)
    server.create_route(ip, dev)

@receiver(pre_delete, sender=MulticastInput)
def MulticastInput_pre_delete(sender, instance, **kwargs):
    "Signal to delete the route"
    server = instance.server
    ip = instance.ip
    dev = server.get_netdev(instance.interface)
    server.delete_route(ip, dev)

class IPOutput(DeviceServer):
    "Generic IP output class"
    class Meta:
        abstract = True
    
    PROTOCOL_CHOICES = (
                        (u'udp', u'UDP'),
                        (u'rtp', u'RTP'),
                        )
    
    interface = models.IPAddressField(_(u'Interface de rede'))
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    protocol = models.CharField(_(u'Protocolo de transporte'), max_length=20,
                                choices=PROTOCOL_CHOICES, default=u'udp')

class MulticastOutput(IPOutput):
    "Multicast MPEG2TS IP output stream"
    class Meta:
        verbose_name = _(u'Saída IP multicast')
        verbose_name_plural = _(u'Saídas IP multicast')
    
    def __unicode__(self):
        return '%s:%d [%s]' % (self.ip, self.port, self.interface)
    
    def validate_unique(self, exclude=None):
        # unique_together = ('ip', 'server')
        from django.core.exceptions import ValidationError
        val = MulticastOutput.objects.filter(ip=self.ip,
                                          server=self.server)
        if val.exists() and val[0].pk != self.pk:
            msg = _(u'Combinação já existente: %s e %s' % (self.server.name, self.ip))
            raise ValidationError({'__all__' : [msg]})
    
    ip = models.IPAddressField(_(u'Endereço IP multicast'))

#class DvbblastProgram(DeviceIp):
#    class Meta:
#        verbose_name = _(u'Programa DVB')
#        verbose_name_plural = _(u'Programas DVB')
#    name = models.CharField(_(u'Nome'),max_length=200)
#    channel_program = models.PositiveSmallIntegerField(_(u'Programa'))
#    channel_pid = models.PositiveSmallIntegerField(_(u'PID (Packet ID)'))
#    src = models.ForeignKey(Dvblast,related_name='source')
#    def __unicode__(self):
#        return self.name

class StreamRecorder(DeviceServer):
    class Meta:
        verbose_name = _(u'Gravador de fluxo')
        verbose_name_plural = _(u'Gravadores de fluxo')
    rotate = models.PositiveIntegerField()
    folder = models.CharField(max_length=500)





class Multicat(DeviceServer):
    """
    DEPRECATED: Não utilizado mais
    Classe generica de fluxo via multicat
    
    Precisa ser implementado _input(self) e _output(self) para que os métodos de
    comando funcionem.
    """
    class Meta:
        verbose_name = _(u'Instancia de Multicat')
        verbose_name_plural = _(u'Instancias de Multicat')
    parans = models.CharField(_(u'Parâmetros extra'),max_length=255,blank=True)
    rtp    = models.BooleanField(_(u'RTP'), default=False)
    def __unicode__(self):
        return '%s -> %s'%(self.input,self.destine)
    def _input(self):
        return ''
    def _output(self):
        return ''
    def start(self):
        """Inicia processo do Multicat"""
        rtp = '-u -U' if not self.rtp else ''
        try:
            c = u'/usr/bin/multicat %s %s %s ' \
                ' >/dev/null 2>&1 & '% (rtp, self._input(), self._output())
            print c
            c = self.server.execute_daemon(c)
            print 'Multicat: %s'%c
            self.status = True
            self.pid = c
        except ValueError:
            print('vlc execute error: %s'%ValueError)
            self.status = False
            self.pid = None
        self.save()
        return self.status
    def stop(self):
        """Interrompe processo"""
        try:
            self.server.execute('kill %s'%self.pid)
            print('Multicat: [stop] %s'%self.pid)
            self.status = False
            self.pid = None
        except ValueError:
            print('vlc execute error: %s'%ValueError)
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
    def switch_link(self):
        if self.status is True:
            url = reverse('device.views.multicat_stop',kwargs={'pk':self.id})
            return '<a href="%s" id="multicat_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('device.views.multicat_start',kwargs={'pk':self.id})
        return '<a href="%s" id="multicat_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
    switch_link.allow_tags = True


#class MulticatGeneric(Multicat):
#    """
#    DEPRECATED: Não utilizado mais
#    Classe para gerar fluxo pelo multicat de origem e destino qualquer
#    """
#    class Meta:
#        verbose_name = _(u'Instancia de Multicat')
#        verbose_name_plural = _(u'Instancias de Multicat')
#    input  = models.CharField(_(u'Input Item'),max_length=255,blank=True)
#    destine = models.CharField(_(u'Destine Item'),max_length=255,blank=True)
#    def _input(self):
#        return u'%s' % (self.input)
#    def _output(self):
#        return u'%s' % (self.destine)
#    def __unicode__(self):
#        return u'%s %s' % (self.input, self.destine)
#
#class MulticatSource(Multicat):
#    """
#    DEPRECATED: Não utilizado mais
#    Classe para gerar fluxo pelo multicat de origem customizada
#    """
#    class Meta:
#        verbose_name = _(u'Instancia de Multicat via IP')
#        verbose_name_plural = _(u'Instancias de Multicat via IP')
#    ip = models.IPAddressField(_(u'Endereço IP'),blank=True)
#    port = models.PositiveSmallIntegerField(_(u'Porta'),blank=True)
#    def _input(self):
#        return u'@%s:%s' % (self.ip, self.port)
#    def _output(self):
#        return u'%s:%s' % (self.target.ip, self.target.port)
#    def __unicode__(self):
#        return u'%s' % self.target
# 
#
#class MulticatRedirect(Multicat):
#    """
#    DEPRECATED: Não utilizado mais
#    Classe para gerar fluxo de redirecionamento via multicat
#    """
#    class Meta:
#        verbose_name = _(u'Instancia de Redirecionamento Multicat')
#        verbose_name_plural = _(u'Instancias de Redirecionamento Multicat')
#    target = models.OneToOneField(IPInput)
#    def _input(self):
#        return u'@%s:%s' % (self.target.source.ip, self.target.source.port)
#    def _output(self):
#        return u'%s:%s' % (self.target.ip, self.target.port)
#    def __unicode__(self):
#        return u'%s' % self.target
#    def switch_link(self):
#        if self.status is True:
#            url = reverse('device.views.multicat_redirect_stop',kwargs={'pk':self.id})
#            return '<a href="%s" id="multicat_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
#        url = reverse('device.views.multicat_redirect_start',kwargs={'pk':self.id})
#        return '<a href="%s" id="multicat_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
#    switch_link.allow_tags = True
#
#
#class MulticatRecorder(models.Model):
#    """
#    DEPRECATED: Não utilizado mais
#    Classe de gravação
#    """
#    class Meta:
#        verbose_name = _(u'Instancia de Multicat para gravação')
#        verbose_name_plural = _(u'Instancias de Multicat para gravação')
#    name = models.CharField(_(u'Nome'),max_length=200)
#    source = models.ForeignKey('Source')
#    rotate_time = models.PositiveIntegerField(_(u'Tempo de gravação em cada arquivo em segundos'))
#    keep_time = models.PositiveSmallIntegerField(_(u'Dias que as gravações estarão disponíveis'))
#    filename = models.CharField(_(u'Nome do arquivo'),max_length=200)
#    server = models.ForeignKey(Server)
#    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)
#    def status(self):
#        url = None
#        return '<a href="%s" id="record_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
#        #return '%s'%self.id
#    status.allow_tags = True
#    def play(self):
#        pass
#    def stop(self):
#        pass
#    def __unicode__(self):
#        return u'%s > %s' %(self.source,self.filename)

