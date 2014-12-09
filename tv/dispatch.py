# -*- encoding:utf8 -*-
from __future__ import absolute_import
# SIGNALS
from django.db.models import signals
from django.conf import settings

from .models import Channel


def channel_post_save(signal, instance, sender, **kwargs):
    """
    Manipulador de evento post-save do Canal
    """
    if instance.image.name.startswith('tv/channel/image/tmp'):
        # Carrega biblioteca de manipulação de imagem
        try:
            import Image
        except ImportError:
            from PIL import Image
        import os
        import shutil
        # Pegar info da logo
        extensao = instance.image.name.split('.')[-1]
        # Busca a configuração MEDIA_ROOT
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        # Caso não exista, cria o diretório
        if os.path.exists(
                os.path.join(MEDIA_ROOT, 'tv/channel/image/thumb')
                ) is False:
            os.mkdir(os.path.join(MEDIA_ROOT, 'tv/channel/image/thumb'))
        if os.path.exists(
                os.path.join(MEDIA_ROOT, 'tv/channel/image/original')
                ) is False:
            os.mkdir(os.path.join(MEDIA_ROOT, 'tv/channel/image/original'))
        # Criação da miniatura
        instance.thumb.name = 'tv/channel/image/thumb/%d.%s' % (
            instance.id, extensao
        )
        thumb = Image.open(instance.image.path)
        thumb.thumbnail((200, 200), Image.ANTIALIAS)
        thumb.save(instance.thumb.path)
        # Imagem original
        original = 'tv/channel/image/original/%d.%s' % (instance.id, extensao)
        shutil.copyfile(instance.image.path, os.path.join(
            MEDIA_ROOT, original)
        )
        # Remove arquivo temporário
        os.unlink(instance.image.path)
        # instance.thumb.file
        instance.image.name = original
        instance.save()


signals.post_save.connect(channel_post_save, sender=Channel)
