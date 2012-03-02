#!/usr/bin/env python
# -*- encoding:utf8 -*-
#from base import *

from django.db import models

from django.utils.translation import ugettext as _

#SIGNALS
from django.db.models import signals
from django.conf import settings

from epg.models import Channel
from stream.models import UniqueIP

class Canal(models.Model):
    """
    Classe de manipulação de Canal de TV
    """
    class Meta:
        ordering = ('numero',)
        verbose_name_plural = _('Canais')
    numero = models.PositiveSmallIntegerField(_('Numero'), unique=True)
    nome   = models.CharField(_('Nome'), max_length=100)
    descricao = models.TextField(_('Descricao'))
    sigla = models.CharField(_('Sigla'), max_length=5)
    logo = models.ImageField(_('Logo'), upload_to='imgs/canal/logo/tmp', 
        help_text='Imagem do canal')
    thumb = models.ImageField(_('Miniatura'),upload_to='imgs/canal/logo/thumb',
        help_text='Imagem do canal')
    source = models.ForeignKey(UniqueIP)
    atualizado = models.DateTimeField(auto_now=True)
    epg = models.ForeignKey(Channel, blank=True, null=True)
    enabled = models.BooleanField(_(u'Disponível'), default=False)
    def __unicode__(self):
        return u"[%d] num=%s %s" %(self.id,self.numero,self.nome)
    
    def imagem_thum(self):
        return u'<img width="40" alt="Thum não existe" src="%s" />' % (
             self.thumb.url)
    imagem_thum.short_description = 'Miniatura'
    imagem_thum.allow_tags = True
    
    def delete(self):
        """
        Limpeza da imagem.
        Remove o logo e o thumbnail ao remover o canal
        """
        super(Canal,self).delete()
        import os
        os.unlink(self.logo.path)
        os.unlink(self.thumb.path)

class Genero(models.Model):
    def __unicode__(self):
        return self.nome
    nome = models.CharField(_('Nome'),max_length=100)

class Programa(models.Model):
    """
    Elemento de um programa na grade
    """
    class Meta:
        ordering = ('hora_inicial',)
    nome = models.CharField(_('Nome'),max_length=100)
    sinopse = models.TextField(_('Sinopse'))
    genero = models.ForeignKey(Genero)
    canal = models.ForeignKey(Canal)
    hora_inicial = models.DateTimeField()
    hora_final = models.DateTimeField()
    def __unicode__(self):
        return self.nome


def canal_post_save(signal, instance, sender, **kwargs):
    """
    Manipulador de evento post-save do Canal
    """
    #print('canal_post_save:%s'%instance)
    #print(instance.logo.url)
    #print('signal:%s'%signal)
    #print('sender:%s'%sender)
    #if instance.logo is None:
    #    return
    if instance.logo.name.startswith('imgs/canal/logo/tmp'):
        ## Carrega biblioteca de manipulação de imagem
        #print('Original:\n%s'%instance.logo.path)
        try:
            import Image
        except ImportError:
            from PIL import Image
        import os,shutil
        ## Pegar info da logo
        extensao = instance.logo.name.split('.')[-1]
        # Busca a configuração MEDIA_ROOT
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        # Caso não exista, cria o diretório
        if os.path.exists(os.path.join(MEDIA_ROOT,'imgs/canal/logo/thumb')) == False:
            os.mkdir(os.path.join(MEDIA_ROOT,'imgs/canal/logo/thumb'))
        if os.path.exists(os.path.join(MEDIA_ROOT,'imgs/canal/logo/original')) == False:
            os.mkdir(os.path.join(MEDIA_ROOT,'imgs/canal/logo/original'))
        # Criação da miniatura
        instance.thumb.name = 'imgs/canal/logo/thumb/%d.%s' %(instance.id,extensao)
        thumb = Image.open(instance.logo.path)
        thumb.thumbnail((200,200),Image.ANTIALIAS)
        thumb.save(instance.thumb.path)
        # Imagem original
        original = 'imgs/canal/logo/original/%d.%s' %(instance.id,extensao)
        #print('Copiando:\n%s\n%s'%(instance.logo.path,os.path.join(MEDIA_ROOT,original)))
        shutil.copyfile(instance.logo.path, os.path.join(MEDIA_ROOT,original))
        # Remove arquivo temporário
        os.unlink(instance.logo.path)
        #instance.thumb.file
        instance.logo.name = original
        instance.save()


signals.post_save.connect(canal_post_save, sender=Canal)
