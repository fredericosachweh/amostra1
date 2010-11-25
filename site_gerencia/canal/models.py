#!/usr/bin/env python
# -*- encoding:utf8 -*-
#from base import *

from django.db import models

from django.utils.translation import ugettext as _

#SIGNALS
from django.db.models import signals

class Canal(models.Model):
    """
    Classe de manipulação de Canal de TV
    """
    class Meta:
        ordering = ('nome',)
        unique_together = ( ('ip','porta'), )
    numero = models.PositiveSmallIntegerField(_('Numero'),unique=True)
    nome = models.CharField(_('Nome'), max_length=100, unique=True)
    def __unicode__(self):
        return "[%s]%s" %(self.numero,self.nome);
    descricao = models.TextField(_('Descricao'))
    logo = models.ImageField(_('Logo'),upload_to='imgs/canal/logo/tmp' ,help_text='Imagem do canal')
    thumb = models.ImageField(_('Miniatura'),upload_to='imgs/canal/logo/thumb' ,help_text='Imagem do canal')
    sigla = models.CharField(_('Sigla'),blank=False,max_length=5)
    ip = models.IPAddressField(_('IP'),blank=False)
    porta = models.PositiveSmallIntegerField(_('Porta'),blank=False)

class Genero(models.Model):
    def __unicode__(self):
        return self.nome
    nome = models.CharField(_('Nome'),max_length=100)

class Programa(models.Model):
    """
    Elemento de um programa na grade
    """
    nome = models.CharField(_('Nome'),max_length=100)
    sinopse = models.TextField(_('Sinopse'))
    genero = models.ForeignKey(Genero)
    canal = models.ForeignKey(Canal)
    hora_inicial = models.DateTimeField()
    hora_final = models.DateTimeField()


def canal_post_save(signal,instance,sender,**kwargs):
    """
    Manipulador de evento post-save do Canal
    """
    pass
    #print('No canal_post_save')
    #print(signal)
    #print(instance)


signals.post_save.connect(canal_post_save, sender=Canal)

