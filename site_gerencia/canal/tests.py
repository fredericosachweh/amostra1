#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
"""

from django.test import TestCase,Client
from django.conf import settings

class CanalTest(TestCase):
    def setUp(self):
        pass

    def test_upload_file(self):
        c = Client()
        l1 = open(settings.MEDIA_ROOT+'/test_files/a.png')
        ## Cria primeiro canal
        c.post('/canal/add/',{
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
        c1 = Canal.objects.get(pk=1)
        self.failUnlessEqual(c1.nome,u'Rede BOBO de Televisão')
        import os
        thumb = settings.MEDIA_ROOT+'/imgs/canal/logo/thumb/%d.png'%c1.id
        exists = os.path.exists(thumb)
        self.failIf( (exists is False) )
        l1.close()




class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
>>> print("Iniciando doctest")
Iniciando doctest
"""}

