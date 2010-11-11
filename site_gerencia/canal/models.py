#!/usr/bin/env python
# -*- encoding:utf8 -*-
from base import *
from django.db import models

from django.utils.translation import ugettext as _

#SIGNALS
#from django.db.models import signals

class Canal(models.Model):
    """
    Classe de manipulação de Canal de TV
    """
    numero = models.PositiveSmallIntegerField(_('Numero'),unique=True)
    nome = models.CharField(_('Nome'), max_length=100, unique=True)
    def __unicode__(self):
        return "[%s]%s" %(self.numero,self.nome);
    descricao = models.CharField(_('Descricao'), blank=False, max_length=255)
    logo = models.ImageField(_('Logo'),upload_to='imgs/canal/logo/original' ,help_text='Imagem do canal')
    thumb = models.ImageField(_('Miniatura'),upload_to='imgs/canal/logo/thumb' ,help_text='Imagem do canal')
    sigla = models.CharField(_('Sigla'),blank=False,max_length=5)
    ip = models.IPAddressField(_('IP'),blank=False)
    porta = models.PositiveSmallIntegerField(_('Porta'),blank=False)


def canal_post_save(signal,instance,sender,**kwargs):
    """
    Manipulador de evento post-save do Canal
    """
    pass


#signals.post_save.connect(canal_post_save, sender=Canal)

