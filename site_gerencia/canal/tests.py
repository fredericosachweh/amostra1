#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.test import TestCase,Client
from django.conf import settings

class CanalTest(TestCase):
    """
    Testes dos canais de televisão
    """
    def setUp(self):
        c = Client()
        i1 = open(settings.MEDIA_ROOT+'/test_files/b.png')
        ## Cria primeiro canal
        c.post('/canal/add/',
               {
              'logo':i1,
              'nome':'Rede SBT',
              'numero':10,
              'descricao':'Silvio Faliu',
              'sigla':'SBT',
              'ip':'224.0.0.10',
              'porta':11000
              })
        i2 = open(settings.MEDIA_ROOT+'/test_files/c.png')
        ## Cria primeiro canal
        c.post('/canal/add/',
               {
              'logo':i2,
              'nome':'Rede SBT 1',
              'numero':11,
              'descricao':'Rede do banco',
              'sigla':'SBT1',
              'ip':'224.0.0.10',
              'porta':11001
              })
        i1.close()
        i2.close()

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
        ## Cria segundo canal
        c.post('/canal/add/',
               {
              'logo':l1,
              'nome':'Rede BOBO de Televisão',
              'numero':13,
              'descricao':'Só para otários',
              'sigla':'BOBO',
              'ip':'224.0.0.10',
              'porta':11002
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
        c.get('/canal/delete/%d'%c1.id)
        existsThum = os.path.exists(thumb)
        existsLogo = os.path.exists(logo)
        self.failIf( (existsThum is True) ,'Thumbnail deveria ser removido')
        self.failIf( (existsLogo is True) ,'Logo deveria ser removido')

    def test_canal_service(self):
        c = Client()
        response = c.get('/canal/canallist/')
        self.failUnlessEqual(response.status_code,200,'Status da lista de canais')
        import simplejson as json
        # Objeto JSON
        decoder = json.JSONDecoder()
        jcanal = decoder.decode(response.content)
        self.failUnlessEqual(len(jcanal['data']),2,'Deveria haver 2 canais')


class ProgramTest(TestCase):
    def setUp(self):
        pass

    def test_program(self):
        pass

