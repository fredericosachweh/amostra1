#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse


class UniqueIP(models.Model):
    """
    Classe para ser extendida, para que origem e destino nunca sejam iguais.
    """
    class Meta:
        unique_together = ( ('ip', 'port'), )
    ip = models.IPAddressField(_(u'Endereço IP'), default='239.0.0.')
    port = models.PositiveSmallIntegerField(_(u'Porta'), default=10000)
    #XXX: Validar IP + PORTA devem ser unico
    def __unicode__(self):
        return '%s:%s' % (self.ip, self.port)
    
    def natural_key(self):
        return {'ip': self.ip,'port': self.port}


class Source(UniqueIP):
    """
    Origem de fluxos, também são destino de devices, cuidar para que apenas 1
    device utilize o fluxo de destino por vez, ou vai dar conflito
    """
    class Meta:
        verbose_name = _(u'Origem de fluxo')
        verbose_name_plural = _(u'Origens de fluxo')
        
    is_rtp = models.BooleanField(_(u'RTP'), default=False)
    desc = models.CharField(_(u'Descrição'), max_length=100, blank=True)
    
    def __unicode__(self):
        rtp = '[RTP]' if self.is_rtp else ''
        desc = '- %s'%(self.desc) if self.desc else ''
        return '%s:%d %s %s' %(self.ip,self.port,rtp,desc)
        #return '%s:%d' %(self.ip,self.port)
    
    def destinations(self):
        return self.destination_set.all()
    
    def in_use(self):
        return bool(self.sourcerelation)
    
    in_use.boolean = True


class SourceRelation(models.Model):
    """
    Modelo que cria relação única com a origem (Source), sempre que for relacionar
    um Device ou qualquer gerador de fluxo de origem, extender este modelo.

    Um fluxo de origem não pode ter mais que uma fonte, senão causará conflito.
    """
    class Meta:
        verbose_name = _(u'Relação')
        verbose_name_plural = _(u'ORelações')
    destine = models.OneToOneField(Source)


class Destination(UniqueIP):
    """
    Destino dos fluxos, aqui deve relacionar para vários channels e outros models
    que consomem fluxos.
    """
    class Meta:
        verbose_name = _(u'Destino de fluxo')
        verbose_name_plural = _(u'Destinos de fluxo')
    source = models.ForeignKey(Source)
    is_rtp = models.BooleanField(_(u'RTP'), default=False)
    recovery_port = models.PositiveSmallIntegerField(
        _(u'Porta de recuperação de pacotes'),
        blank=True,
        null=True)
    desc = models.CharField(_(u'Descrição'),max_length=100,blank=True)
    
    def __unicode__(self):
        rtp = '[RTP]' if self.is_rtp else ''
        r_port = ' - (%s)' %(self.recovery_port) if self.recovery_port else ''
        desc = '- %s'%(self.desc) if self.desc else ''
        return '%s > %s:%d %s %s %s' %(
            self.source,
            self.ip,
            self.port,
            rtp,
            r_port,
            desc
            )



class Server(models.Model):
    """Servidores e caracteristicas de conexão"""

    class Meta:
        verbose_name = _(u'Servidor de Recursos')
        verbose_name_plural = _(u'Servidores de Recursos')

    name = models.CharField(_(u'Nome'), max_length=200, unique=True)
    host = models.IPAddressField(_(u'Host'), blank=True, unique=True)
    username = models.CharField(_(u'Usuário'), max_length=200 ,blank=True)
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
    SERVER_TYPE_CHOICES=(
                         (u'local', _(u'Servidor local DEMO')),
                         (u'dvb', _(u'Sintonizador DVB')),
                         (u'recording', _(u'Servidor TVoD')),
                         )
    server_type = models.CharField(_(u'Tipo de Servidor'), max_length=100, 
                                   choices=SERVER_TYPE_CHOICES)

    def __unicode__(self):
        return '%s' %(self.name)

    def switch_link(self):
        url = reverse('device.views.server_status', kwargs={'pk': self.id})
        return '<a href="%s" id="server_id_%s" >Atualizar</a>' % (url, self.id)

    switch_link.allow_tags = True
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if str(self.server_type) == 'local' and str(self.host) != '127.0.0.1':
            raise ValidationError(_(u'Servidor DEMO só pode ser usado com IP local 127.0.0.1.'))
    
    @property    
    def is_local(self):
        return True if str(self.server_type) == 'local' else False

    def connect(self):
        """Conecta-se ao servidor"""
        from lib import ssh
        s = None
        try:
            s = ssh.Connection(host = self.host,
                port = self.ssh_port,
                username = self.username,
                password = self.password,
                private_key = self.rsakey)
            self.status = True
            self.msg = 'OK'
        except ValueError:
            self.status = False
            self.msg = ValueError
        self.save()
        return s

    def execute(self, command, persist = False):
        """Executa um comando no servidor"""
        #stdin, stdout, stderr = None,None,None
        try:
            s = self.connect()
            self.msg = 'OK'
        except:
            pass
        try:
            w = s.execute(command)
        except Exception as ex:
            self.msg = ex
            print('command: [%s] %s'%(command,self.msg))
        if not persist:
            s.close()
        self.save()
        return w

    def execute_daemon(self,command):
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

    def process_alive(self,pid):
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
            ret.append(
                {'pid': int(cmd[0]), 'name': cmd[1], 'command': ' '.join(cmd[2:])}
                )
        return ret

    def kill_process(self,pid):
        s = self.connect()
        resp = s.execute('/bin/kill %d' % pid)
        s.close()
        return resp


class DeviceIp(SourceRelation):
    """Campos para servidor de Device"""
    description = models.CharField(_(u'Descrição'),blank=True,max_length=255)
    def __unicode__(self):
        return '[%s] %s' %(self.server,self._type,self.description)
    def _type(self):
        return _(u'indefinido')


class DeviceServer(models.Model):
    """Relaciona IP com servidor de Device!"""
    server = models.ForeignKey(Server, verbose_name=_(u'Servidor de recursos'))
    status = models.BooleanField(_(u'Status'),default=False,editable=False)
    pid = models.PositiveSmallIntegerField(_(u'PID'),blank=True,null=True,editable=False)
#    def __unicode__(self):
#        return '[%s] %s' % (self.server, self._type)
    def _type(self):
        return _(u'indefinido')

class Vlc(DeviceIp,DeviceServer):
    """VLC streaming device"""
    class Meta:
        verbose_name = _(u'Vídeo em loop')
        verbose_name_plural = _(u'Vídeos em loop')
    source = models.CharField(_(u'Origem'),max_length=255)
    def __unicode__(self):
        return '[%s] %s > %s' %(self.server,self.destine,self.description)

    def start(self):
        """Inicia processo do VLC"""
        s = self.source.replace(' ','\ ').replace("'","\\'").replace('(','\(').replace(')','\)')
        c = '/usr/bin/cvlc -I dummy -v -R %s ' \
            '--sout "#std{access=udp,mux=ts,dst=%s:%d}"' % (
            s,
            self.destine.ip,
            self.destine.port)
        print c
        c = self.server.execute_daemon(c)
        self.status = True
        self.pid = c
        self.save()
        return self.status

    def stop(self):
        """Interrompe processo do VLC"""
        try:
            self.server.kill_process(self.pid)
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
            alive = self.server.process_alive(self.pid)
        else:
            alive = False
        if alive:
            url = reverse('device.views.vlc_stop',kwargs={'pk':self.id})
            return '<a href="%s" id="vlc_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('device.views.vlc_start',kwargs={'pk':self.id})
        return '<a href="%s" id="vlc_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
    switch_link.allow_tags = True


class Dvblast(DeviceServer):
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
    def stop(self):
        'Para o fluxo (mata o processo do multicat)'
        from lib.player import Player
        p = Player()
        p.stop_stream(self)
        self.pid = None
        self.save()
    def autostart(self):
        if self.pid is not None:
            from lib.player import Player
            p = Player()
            if p.is_playing(self) is False:
                self.play()

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
        (u'H', u'Horizontal (H)'),
        (u'V', u'Vertical (V)'),
        (u'R', u'Direita (R)'),
        (u'L', u'Esquerda (L)'),
    )
    
    symbol_rate = models.PositiveIntegerField(_(u'Taxa de símbolos'), help_text=u'Msym/s')
    modulation = models.CharField(_(u'Modulação'), max_length=200, choices=MODULATION_CHOICES)
    polarization = models.CharField(_(u'Polarização'), max_length=200, choices=POLARIZATION_CHOICES)
    adapter = models.CharField(_(u'Adaptador'), max_length=200)
    antenna = models.ForeignKey(Antenna, verbose_name=_(u'Antena'))

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

class DvbblastProgram(DeviceIp):
    class Meta:
        verbose_name = _(u'Programa DVB')
        verbose_name_plural = _(u'Programas DVB')
    name = models.CharField(_(u'Nome'),max_length=200)
    channel_program = models.PositiveSmallIntegerField(_(u'Programa'))
    channel_pid = models.PositiveSmallIntegerField(_(u'PID (Packet ID)'))
    source = models.ForeignKey(Dvblast,related_name='source')
    def __unicode__(self):
        return self.name

class Multicat(DeviceServer):
    """
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

class MulticatGeneric(Multicat):
    """
    Classe para gerar fluxo pelo multicat de origem e destino qualquer
    """
    class Meta:
        verbose_name = _(u'Instancia de Multicat')
        verbose_name_plural = _(u'Instancias de Multicat')
    input  = models.CharField(_(u'Input Item'),max_length=255,blank=True)
    destine = models.CharField(_(u'Destine Item'),max_length=255,blank=True)
    def _input(self):
        return u'%s' % (self.input)
    def _output(self):
        return u'%s' % (self.destine)
    def __unicode__(self):
        return u'%s %s' % (self.input, self.destine)

class MulticatSource(Multicat,DeviceIp):
    """
    Classe para gerar fluxo pelo multicat de origem customizada
    """
    class Meta:
        verbose_name = _(u'Instancia de Multicat via IP')
        verbose_name_plural = _(u'Instancias de Multicat via IP')
    ip = models.IPAddressField(_(u'Endereço IP'),blank=True)
    port = models.PositiveSmallIntegerField(_(u'Porta'),blank=True)
    def _input(self):
        return u'@%s:%s' % (self.ip, self.port)
    def _output(self):
        return u'%s:%s' % (self.target.ip, self.target.port)
    def __unicode__(self):
        return u'%s' % self.target
 

class MulticatRedirect(Multicat,DeviceIp):
    """
    Classe para gerar fluxo de redirecionamento via multicat
    """
    class Meta:
        verbose_name = _(u'Instancia de Redirecionamento Multicat')
        verbose_name_plural = _(u'Instancias de Redirecionamento Multicat')
    target = models.OneToOneField(Destination)
    def _input(self):
        return u'@%s:%s' % (self.target.source.ip, self.target.source.port)
    def _output(self):
        return u'%s:%s' % (self.target.ip, self.target.port)
    def __unicode__(self):
        return u'%s' % self.target
    def switch_link(self):
        if self.status is True:
            url = reverse('device.views.multicat_redirect_stop',kwargs={'pk':self.id})
            return '<a href="%s" id="multicat_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('device.views.multicat_redirect_start',kwargs={'pk':self.id})
        return '<a href="%s" id="multicat_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
    switch_link.allow_tags = True

class MulticatRecorder(models.Model):
    """
    Classe de gravação
    """
    class Meta:
        verbose_name = _(u'Instancia de Multicat para gravação')
        verbose_name_plural = _(u'Instancias de Multicat para gravação')
    name = models.CharField(_(u'Nome'),max_length=200)
    source = models.ForeignKey('Source')
    rotate_time = models.PositiveIntegerField(_(u'Tempo de gravação em cada arquivo em segundos'))
    keep_time = models.PositiveSmallIntegerField(_(u'Dias que as gravações estarão disponíveis'))
    filename = models.CharField(_(u'Nome do arquivo'),max_length=200)
    server = models.ForeignKey(Server)
    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)
    def status(self):
        url = None
        return '<a href="%s" id="record_id_%s" style="color:red;" >Parado</a>'%(url,self.id)
        #return '%s'%self.id
    status.allow_tags = True
    def play(self):
        pass
    def stop(self):
        pass
    def __unicode__(self):
        return u'%s > %s' %(self.source,self.filename)

