#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django import forms
import canal
from django.conf import settings


class CanalForm(forms.ModelForm):

    class Meta:
        model = canal.models.Canal
        fields = ('numero','nome','descricao','logo','sigla','ip','porta',)
    ## Overload do save
    def save(self,*args,**kwargs):
        """Cria o thumbnail do logo"""
        canal = super(CanalForm,self).save(*args,**kwargs)
        if 'logo' in self.changed_data:
            ## Carrega biblioteca de manipulação de imagem
            try:
                import Image
            except ImportError:
                from PIL import Image
            import os,shutil
            ## Pegar info da logo
            extensao = canal.logo.name.split('.')[-1]
            # Busca a configuração MEDIA_ROOT
            MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
            # Caso não exista, cria o diretório
            if os.path.exists(MEDIA_ROOT+'/imgs/canal/logo/thumb/') == False:
                os.mkdir(MEDIA_ROOT+'/imgs/canal/logo/thumb/')
            if os.path.exists(MEDIA_ROOT+'/imgs/canal/logo/original/') == False:
                os.mkdir(MEDIA_ROOT+'/imgs/canal/logo/original/')
            # Criação da miniatura
            canal.thumb.name = 'imgs/canal/logo/thumb/%d.%s' %(canal.id,extensao)
            thumb = Image.open(canal.logo.path)
            thumb.thumbnail((100,100),Image.ANTIALIAS)
            thumb.save(canal.thumb.path)
            # Imagem original
            original = 'imgs/canal/logo/original/%d.%s' %(canal.id,extensao)
            shutil.copyfile(canal.logo.path,MEDIA_ROOT+'/'+original)
            # Remove arquivo temporário
            #print('Caminho:%s'%canal.logo.path)
            os.unlink(canal.logo.path)
            canal.thumb.file
            canal.logo.name = original
            canal.save()
        return canal



