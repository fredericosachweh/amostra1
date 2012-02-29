#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from stream import models as stream
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

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

    def __unicode__(self):
        return '%s' %(self.name)

    def switch_link(self):
        url = reverse('device.views.server_status', kwargs={'pk': self.id})
        return '<a href="%s" id="server_id_%s" >Atualizar</a>' % (url, self.id)

    switch_link.allow_tags = True

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
            return None
        try:
            w = s.execute(command)
        except Exception as ex:
            self.msg = ValueError
            print('command: [%s] %s'%(command,self.msg))
        if not persist:
            s.close()
        self.save()
        return w

    def execute_daemon(self,command):
        pid = -1
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
                print('process_alive:%s' % p)
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


class Vlc(stream.SourceRelation):
    """VLC streaming device"""

    class Meta:
        verbose_name = _(u'Trailer')
        verbose_name_plural = _(u'Trailers')
    description = models.CharField(_(u'Descrição'),blank=True,max_length=255)
    source = models.CharField(_(u'Origem'),max_length=255)
    server = models.ForeignKey(Server)
    status = models.BooleanField(_(u'Status'),default=False,editable=False)
    pid = models.PositiveSmallIntegerField(_(u'PID'),blank=True,null=True,editable=False)

    def __unicode__(self):
        return '[%s] %s > %s' %(self.server,self.source,self.destine)

    def start(self):
        """Inicia processo do VLC"""
        c = self.server.execute_daemon('/usr/bin/cvlc -I dummy -v -R %s ' \
            '--sout "#std{access=udp,mux=ts,dst=%s:%d}"' % (
            self.source,
            self.destine.ip,
            self.destine.port)
        )
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
            url = reverse('device.views.vlc_stop',kwargs={'pk':self.id})
            return '<a href="%s" id="vlc_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('device.views.vlc_start',kwargs={'pk':self.id})
        return '<a href="%s" id="vlc_id_%s" style="color:red;" >Parado</a>'%(url,self.id)

    switch_link.allow_tags = True


class Dvblast(models.Model):

    class Meta:
        verbose_name = _(u'DVBlast')
        verbose_name_plural = _(u'DVBlast')

    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    is_rtp = models.BooleanField(_(u'RTP'),default=False)
    server = models.ForeignKey(Server)
    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)

    def __unicode__(self):
        return '%s (%s:%s)' %(self.name,self.ip,self.port)

    def status(self):
        from lib.player import Player
        p = Player()
        if p.is_playing(self) is True:
            url = reverse('stream.views.stop',kwargs={'streamid':self.id})
            return '<a href="%s" id="stream_id_%s" style="color:green;cursor:pointer;" >Rodando</a>' %(url,self.id)
        url = reverse('stream.views.play',kwargs={'streamid':self.id})
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

class DvbblastProgram(stream.SourceRelation):

    class Meta:
        verbose_name = _(u'Programa DVB')
        verbose_name_plural = _(u'Programas DVB')

    name = models.CharField(_(u'Nome'),max_length=200)
    channel_program = models.PositiveSmallIntegerField(_(u'Programa'))
    channel_pid = models.PositiveSmallIntegerField(_(u'PID (Packet ID)'))
    source = models.ForeignKey(Dvblast,related_name='origem')
    def __unicode__(self):
        return self.name

class Multicat(stream.SourceRelation):
    """
    Classe para gerar fluxo pelo multicat ou redireciona-lo
    """

    class Meta:
        verbose_name = _(u'Instancia de Multicat')
        verbose_name_plural = _(u'Instancias de Multicat')
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    parans = models.CharField(_(u'Parâmetros extra'),max_length=255,blank=True)
    server = models.ForeignKey(Server)
    status = models.BooleanField(_(u'Status'),default=False,editable=False)
    pid = models.PositiveSmallIntegerField(_(u'PID'),blank=True,null=True,editable=False)
    def __unicode__(self):
        return '%s:%s -> %s'%(self.ip,self.port,self.destine)
    def start(self):
        """Inicia processo do Multicat"""
        try:
            c = self.server.execute('/usr/bin/multicat -u -U @%s:%s %s ' \
                ' >/dev/null 2>&1 & '%
                                    (self.ip, self.port, self.destine), persist=True)
            print 'Multicat: %s'%c
            c = self.server.execute('echo $@')
            print 'Multicat: %s'%c
            self.status = True
            self.pid = c[0]
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

class MulticatRecorder(models.Model):
    """
    Classe de gravação
    """
    class Meta:
        verbose_name = _(u'Instancia de Multicat para gravação')
        verbose_name_plural = _(u'Instancias de Multicat para gravação')
    name = models.CharField(_(u'Nome'),max_length=200)
    source = models.ForeignKey('stream.Source')
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

