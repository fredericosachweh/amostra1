#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

class MediaMulticastSource(models.Model):
    class Meta:
        verbose_name = _(u'Origem de fluxo')
        verbose_name_plural = _(u'Origens de fluxo')
    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'))
    port = models.PositiveSmallIntegerField(_(u'Porta'))
    is_rtp = models.BooleanField(_(u'É RTP'),default=False)
    def __unicode__(self):
        return '%s (%s:%s)' %(self.name,self.ip,self.port)

class MediaMulticastDestination(models.Model):
    class Meta:
        verbose_name = _(u'Destino de fluxo')
        verbose_name_plural = _(u'Destinos de fluxo')
    name = models.CharField(_(u'Nome'),max_length=200)
    ip = models.IPAddressField(_(u'Endereço IP'),blank=True)
    port = models.PositiveSmallIntegerField(_(u'Porta'),blank=True,null=True)
    ip_bind = models.IPAddressField(_(u'Endereço IP de conexão'),blank=True,null=True)
    port_bind = models.PositiveSmallIntegerField(_(u'Porta de conexão'),blank=True,null=True)
    is_rtp = models.BooleanField(_(u'É RTP'),default=False)
    recovery_port = models.PositiveSmallIntegerField(_(u'Porta de recuperação de pacotes'),blank=True,null=True)
    def __unicode__(self):
        return '%s (%s:%d)' %(self.name,self.ip,self.port)

class MediaRecord(models.Model):
    class Meta:
        verbose_name = _(u'Destino de gravação')
        verbose_name_plural = _(u'Destino de Gravações')
    name = models.CharField(_(u'Nome'),max_length=200)
    rotate_time = models.PositiveIntegerField(_(u'Tempo de gravação em cada arquivo em segundos'))
    keep_time = models.PositiveSmallIntegerField(_(u'Dias que as gravações estarão disponíveis'))
    filename = models.CharField(_(u'Nome do arquivo'),max_length=200)
    def __unicode__(self):
        return self.name

class Record(models.Model):
    class Meta:
        verbose_name = _(u'Gravação')
        verbose_name_plural = _(u'Gravações')
    source = models.ForeignKey(MediaMulticastSource)
    filename = models.ForeignKey(MediaRecord)
    def play(self):
        pass
    def stop(self):
        pass

class Stream(models.Model):
    """
    Classe responsável pelo controle de fluxos multicast entre source (origem)
    e destination (destino)
    """
    class Meta:
        verbose_name = _(u'Fluxo')
        verbose_name_plural = _(u'Fluxos')
    source = models.ForeignKey(MediaMulticastSource)
    destination = models.ForeignKey(MediaMulticastDestination, unique=True)
    pid = models.PositiveSmallIntegerField(u'PID',blank=True,null=True)
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
    def __unicode__(self):
        return '%s %s:%d -> %s %s:%d' %(self.source.name,self.source.ip,self.source.port,self.destination.name,self.destination.ip,self.destination.port)
    def play(self):
        from stream.player import Player
        p = Player()
        pid = p.play_stream(self)
        self.pid = pid
        self.save()
        


