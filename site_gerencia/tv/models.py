#!/usr/bin/env python
# -*- encoding:utf8 -*-
#from base import *

from django.db import models

from django.utils.translation import ugettext as _

#SIGNALS
from django.db.models import signals
from django.conf import settings

from device.models import UniqueIP

class Channel(models.Model):
    """
    Classe de manipulação de Canal de TV
    """
    class Meta:
        ordering = ('number',)
        verbose_name_plural = _('Canais')
    number      = models.PositiveSmallIntegerField(_('Numero'), unique=True)
    name        = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descricao'))
    channelid   = models.CharField(_('ID do Canal'), max_length=255)
    image       = models.ImageField(_('Logo'), 
        upload_to = 'tv/channel/image/tmp', 
        help_text = 'Imagem do canal'
    )
    thumb       = models.ImageField(_('Miniatura'),
        upload_to = 'tv/channel/image/thumb',
        help_text = 'Imagem do canal'
    )
    source      = models.OneToOneField(UniqueIP, unique=True, null=True, blank=True)
    updated     = models.DateTimeField(auto_now=True)
    enabled     = models.BooleanField(_(u'Disponível'), default=False)
    
    def __unicode__(self):
        return u"[%d] num=%s %s" %(self.id,self.number,self.name)
    
    def image_thum(self):
        return u'<img width="40" alt="Thum não existe" src="%s" />' % (
             self.thumb.url)
    
    image_thum.short_description = 'Miniatura'
    image_thum.allow_tags = True
    
    def delete(self):
        """
        Limpeza da imagem.
        Remove o logo e o thumbnail ao remover o canal
        """
        super(Canal,self).delete()
        import os
        os.unlink(self.image.path)
        os.unlink(self.thumb.path)
    



def channel_post_save(signal, instance, sender, **kwargs):
    """
    Manipulador de evento post-save do Canal
    """
    #print('canal_post_save:%s'%instance)
    #print(instance.logo.url)
    #print('signal:%s'%signal)
    #print('sender:%s'%sender)
    #if instance.logo is None:
    #    return
    if instance.image.name.startswith('tv/channel/image/tmp'):
        ## Carrega biblioteca de manipulação de imagem
        #print('Original:\n%s'%instance.logo.path)
        try:
            import Image
        except ImportError:
            from PIL import Image
        import os,shutil
        ## Pegar info da logo
        extensao = instance.image.name.split('.')[-1]
        # Busca a configuração MEDIA_ROOT
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        # Caso não exista, cria o diretório
        if os.path.exists(os.path.join(MEDIA_ROOT,'tv/channel/image/thumb')) == False:
            os.mkdir(os.path.join(MEDIA_ROOT,'tv/channel/image/thumb'))
        if os.path.exists(os.path.join(MEDIA_ROOT,'tv/channel/image/original')) == False:
            os.mkdir(os.path.join(MEDIA_ROOT,'tv/channel/image/original'))
        # Criação da miniatura
        instance.thumb.name = 'tv/channel/image/thumb/%d.%s' %(instance.id,extensao)
        thumb = Image.open(instance.image.path)
        thumb.thumbnail((200,200),Image.ANTIALIAS)
        thumb.save(instance.thumb.path)
        # Imagem original
        original = 'tv/channel/image/original/%d.%s' %(instance.id,extensao)
        #print('Copiando:\n%s\n%s'%(instance.logo.path,os.path.join(MEDIA_ROOT,original)))
        shutil.copyfile(instance.image.path, os.path.join(MEDIA_ROOT,original))
        # Remove arquivo temporário
        os.unlink(instance.image.path)
        #instance.thumb.file
        instance.image.name = original
        instance.save()


signals.post_save.connect(channel_post_save, sender=Channel)
