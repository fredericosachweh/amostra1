#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
"""

from django.test import TestCase,Client
from django.conf import settings

class CanalTest(TestCase):
    def setUp(self):
        pass

    def test_required_components(self):
        Image = None
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                pass
        self.failIf(Image is None, 'Biblioteca Image necessária, tente instalar o pacote python-imaging')

    def test_upload_file(self):
        c = Client()
        l1 = open(settings.MEDIA_ROOT+'/test_files/a.png')
        ## Cria primeiro canal
        c.post('/canal/add/',
               {
              'logo':l1,
              'nome':'Rede BOBO de Televisão',
              'numero':13,
              'descricao':'Só para otários',
              'sigla':'BOBO',
              'ip':'224.0.0.10',
              'porta':11000
              })
        from models import Canal
        # Busca o canal criado
        c1 = Canal.objects.get(numero=13)
        self.failIfEqual(c1 is None,'Canal não foi criado')
        self.failUnlessEqual(c1.nome,u'Rede BOBO de Televisão')
        import os
        thumb = settings.MEDIA_ROOT+'/imgs/canal/logo/thumb/%d.png'%c1.id
        logo = settings.MEDIA_ROOT+'/imgs/canal/logo/original/%d.png'%c1.id
        existsThum = os.path.exists(thumb)
        existsLogo = os.path.exists(logo)
        self.failIf( (existsThum is False) ,'Thumbnail não foi criado')
        self.failIf( (existsLogo is False) ,'Logo não foi criado')
        l1.close()
        ## Limpeza
        c.get('/canal/delete/1')
        existsThum = os.path.exists(thumb)
        existsLogo = os.path.exists(logo)
        self.failIf( (existsThum is True) ,'Thumbnail deveria ser removido')
        self.failIf( (existsLogo is True) ,'Logo deveria ser removido')





class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
>>> print("Iniciando doctest")
Iniciando doctest
"""}

