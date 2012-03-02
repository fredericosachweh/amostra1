#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

class UniqueIP(models.Model):
    """
    Classe para ser extendida, para que origem e destino nunca sejam iguais.
    """
    class Meta:
        unique_together = ( ('ip', 'port'), )
    ip = models.IPAddressField(_(u'Endereço IP'),default='239.0.0.')
    port = models.PositiveSmallIntegerField(_(u'Porta'),default=10000)
    #XXX: Validar IP + PORTA devem ser unico
    def __unicode__(self):
        return '%s:%s'%(self.ip,self.port)

class Source(UniqueIP):
    """
    Origem de fluxos, também são destino de devices, cuidar para que apenas 1
    device utilize o fluxo de destino por vez, ou vai dar conflito
    """
    class Meta:
        verbose_name = _(u'Origem de fluxo')
        verbose_name_plural = _(u'Origens de fluxo')
    is_rtp = models.BooleanField(_(u'RTP'),default=False)
    desc = models.CharField(_(u'Descrição'),max_length=100,blank=True)
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
    is_rtp = models.BooleanField(_(u'RTP'),default=False)
    recovery_port = models.PositiveSmallIntegerField(_(u'Porta de recuperação de pacotes'),blank=True,null=True)
    desc = models.CharField(_(u'Descrição'),max_length=100,blank=True)
    def __unicode__(self):
        rtp = '[RTP]' if self.is_rtp else ''
        r_port = ' - (%s)' %(self.recovery_port) if self.recovery_port else ''
        desc = '- %s'%(self.desc) if self.desc else ''
        return '%s > %s:%d %s %s %s' %(self.source,self.ip,self.port,rtp,r_port,desc)





