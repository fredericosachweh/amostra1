#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.test import TestCase,Client
from django.conf import settings

#import pdb
#pdb.set_trace()


class CanalTest(TestCase):
    """
    Testes dos canais de televisão
    """

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
        from models import Canal
        Canal.objects.all().delete()
        c = Client()
        l1 = open(settings.MEDIA_ROOT+'/test_files/a.png')
        ## Cria segundo canal
        c.post('/canal/add/',
               {
              'logo':l1,
              'nome':'Rede BOBO de Televisão',
              'numero':13,
              'descricao':'Só para',
              'sigla':'BOBO',
              'ip':'224.0.0.12',
              'porta':11002
              })
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
        #response = c.get('/canal/delete/%d'%c1.id)
        #self.failUnlessEqual(response.status_code,302,'Deveria redirecionar após remoção')
        #existsThum = os.path.exists(thumb)
        #existsLogo = os.path.exists(logo)
        #self.failIf( (existsThum is True) ,'Thumbnail deveria ser removido')
        #self.failIf( (existsLogo is True) ,'Logo deveria ser removido')

    def test_canal_service(self):
        from models import Canal
        Canal.objects.all().delete()
        c = Client()
        ## Autenticação
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
              'ip':'224.0.0.11',
              'porta':11001
              })
        i1.close()
        i2.close()
        response = c.get('/box/canal_list/')
        self.failUnlessEqual(response.status_code,200,'Status da lista de canais')
        import simplejson as json
        # Objeto JSON
        decoder = json.JSONDecoder()
        jcanal = decoder.decode(response.content)
        self.failUnlessEqual(len(jcanal['data']),2,'Deveria haver 2 canais')
        for canal in jcanal['data']:
            #print(canal)
            response = c.get('/canal/delete/%d'%canal['pk'])
            self.failUnlessEqual(response.status_code,302,'Deveria redirecionar após remoção')




class ProgramTest(TestCase):
    def setUp(self):
        pass

    def test_program(self):
        pass

