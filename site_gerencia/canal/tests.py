#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.conf import settings
from django.test import TestCase,Client
from django.conf import settings

from django.core.urlresolvers import reverse

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
        #Canal.objects.all().delete()
        c = Client()
        l1 = open('canal/fixtures/test_files/a.png')
        url_add = reverse('canal.views.add')
        ## Cria segundo canal
        response = c.post(url_add,
               {
              'logo':l1,
              'nome':'Rede BOBO de Televisão',
              'numero':13,
              'descricao':'Só para',
              'sigla':'BOBO',
              'ip':'224.0.0.12',
              'porta':11002
              })
        self.assertEqual(response.status_code,302,'O código de retorno deveria ser 302 (Redirecionamento)')
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
        url_del = reverse('canal.views.delete',args=[c1.id])
        response = c.get(url_del)
        self.failUnlessEqual(response.status_code,302,'Deveria redirecionar após remoção')
        print('path thumb:%s'%thumb)
        print('path logo:%s'%logo)
        existsThum = os.path.exists(thumb)
        existsLogo = os.path.exists(logo)
        self.failIf( (existsThum is True) ,'Thumbnail deveria ser removido')
        self.failIf( (existsLogo is True) ,'Logo deveria ser removido')

    def test_canal_service(self):
        #from models import Canal
        #Canal.objects.all().delete()
        return
        c = Client()
        ## Carga da imagem
        i1 = open('canal/fixtures/test_files/b.png')
        ## Cria primeiro canal
        url_add = reverse('canal.views.add')
        response = c.post(url_add,
               {
              'logo':i1,
              'nome':'Rede SBT',
              'numero':10,
              'descricao':'Silvio Faliu',
              'sigla':'SBT',
              'ip':'224.0.0.10',
              'porta':11000
              })
        self.assertEqual(response.status_code,302,'O código de retorno deveria ser 302 (Redirecionamento)')
        i2 = open('canal/fixtures/test_files/c.png')
        ## Cria primeiro canal
        response = c.post(url_add,
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
        self.assertEqual(response.status_code,302,'O código de retorno deveria ser 302 (Redirecionamento)')
        ## url da lista de canais -> movido para o app box
        list_url = reverse('box.views.canal_list')
        response = c.get(list_url)
        self.failUnlessEqual(response.status_code,200,'Status da lista de canais')
        import simplejson as json
        # Objeto JSON
        decoder = json.JSONDecoder()
        jcanal = decoder.decode(response.content)
        self.failUnlessEqual(len(jcanal),2,'Deveria haver 2 canais')
        import os
        for canal in jcanal:
            url_delete = reverse('canal.views.delete',args=[canal['pk']])
            response = c.get(url_delete)
            self.failUnlessEqual(response.status_code,302,'Deveria redirecionar após remoção')
            thumb = settings.MEDIA_ROOT+'/imgs/canal/logo/thumb/%d.png'%canal['pk']
            logo = settings.MEDIA_ROOT+'/imgs/canal/logo/original/%d.png'%canal['pk']
            existsThum = os.path.exists(thumb)
            existsLogo = os.path.exists(logo)
            self.failIf( (existsThum is False) ,'Thumbnail não foi criado')
            self.failIf( (existsLogo is False) ,'Logo não foi criado')


