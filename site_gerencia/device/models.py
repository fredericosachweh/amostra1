#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from stream import models as stream
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from lib.pexpect import pxssh
import time

class Server(models.Model):
    """
    Servidores e caracteristicas de conexão
    """
    class Meta:
        verbose_name = _(u'Servidor de Recursos')
        verbose_name_plural = _(u'Servidores de Recursos')
    name = models.CharField(_(u'Nome'),max_length=100,unique=True)
    ip = models.IPAddressField(_(u'Endereço IP'),blank=True,unique=True)
    username = models.CharField(_(u'Usuário'),max_length=200,blank=True)
    password = models.CharField(_(u'Senha'),max_length=200,blank=True)
    rsakey = models.TextField(_(u'Chave RSA'),blank=True)
    ssh_port = models.PositiveSmallIntegerField(_(u'Porta SSH'),blank=True,null=True,default=22)
    status_time = models.DateTimeField(_(u'Data do último status'),blank=True,null=True)
    status = models.BooleanField(_(u'Status'),default=False)
    error = models.CharField(_(u'Mensagem de erro'),max_length=255,blank=True)
    def __unicode__(self):
        return '%s' %(self.name)
    def statusUpdate(self):
        """Faz conexão com servidor e valida se esta foi feita com sucesso, então
        atualiza informações de status_time, status e/ou error"""
        print 'pxssh statusUpdate: %s' %(self)
        s = pxssh.pxssh()
        print 'login: %s %s %s' %(self.ip, self.username, self.password)
        s.login(self.ip, self.username, self.password)
        time.sleep(0.5)
        print 'comando uptime'
        s.sendline('uptime')
        time.sleep(0.5)
        print s.before

class Vlc(stream.SourceRelation):
    """
    VLC streaming device
    """
    class Meta:
        verbose_name = _(u'VLC')
        verbose_name_plural = _(u'VLC\'s')
    description = models.CharField(_(u'Descrição'),blank=True,max_length=255)
    source = models.CharField(_(u'Origem'),max_length=255)
    server = models.ForeignKey(Server)
    status = models.BooleanField(_(u'Status'),default=False)
    pid = models.PositiveSmallIntegerField(_(u'PID'),blank=True,null=True)
    def __unicode__(self):
        return '[%s] %s > %s' %(self.server,self.source,self.destine)
    def status(self):
        pass

class Dvblast(models.Model):
    class Meta:
        verbose_name = _(u'DVBlast')
    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    is_rtp = models.BooleanField(_(u'RTP'),default=False)
    server = models.ForeignKey(Server)
    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)
    def __unicode__(self):
        return '%s (%s:%s)' %(self.name,self.ip,self.port)
    def status(self):
        from stream.player import Player
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
        from stream.player import Player
        p = Player()
        pid = p.play_stream(self)
        self.pid = pid
        self.save()
    def stop(self):
        'Para o fluxo (mata o processo do multicat)'
        from stream.player import Player
        p = Player()
        p.stop_stream(self)
        self.pid = None
        self.save()
    def autostart(self):
        if self.pid is not None:
            from stream.player import Player
            p = Player()
            if p.is_playing(self) is False:
                self.play()

class DvbblastProgram(stream.SourceRelation):
    class Meta:
        verbose_name = _(u'Programa no pacote de fluxo DVB')
        verbose_name_plural = _(u'Programas no pacote de fluxo DVB')
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
        verbose_name = _(u'Instancia de Multicat para redirecionar fluxo')
        verbose_name_plural = _(u'Instancias de Multicat para redirecionar fluxos')
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    parans = models.CharField(_(u'Parâmetros extra'),max_length=255,blank=True)

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