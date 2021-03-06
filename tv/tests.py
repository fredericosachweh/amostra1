#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
import os
import logging

from django.apps import apps
from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.conf import settings
from client import models as clientmodels

log = logging.getLogger('unittest')


@override_settings(DVBLAST_COMMAND=settings.DVBLAST_DUMMY)
@override_settings(DVBLASTCTL_COMMAND=settings.DVBLASTCTL_DUMMY)
@override_settings(MULTICAT_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(MULTICATCTL_COMMAND=settings.MULTICATCTL_DUMMY)
@override_settings(VLC_COMMAND=settings.VLC_DUMMY)
class ChannelTest(TestCase):
    """
    Testes dos canais de televisão
    """

    def setUp(self):
        import getpass
        from django.contrib.auth.models import User
        Server = apps.get_model('device', 'Server')
        NIC = apps.get_model('device', 'NIC')
        UnicastInput = apps.get_model('device', 'UnicastInput')
        UniqueIP = apps.get_model('device', 'UniqueIP')
        MulticastOutput = apps.get_model('device', 'MulticastOutput')
        DemuxedService = apps.get_model('device', 'DemuxedService')
        Storage = apps.get_model('device', 'Storage')
        StreamRecorder = apps.get_model('device', 'StreamRecorder')
        Channel = apps.get_model('tv', 'Channel')

        self.user = User.objects.create_superuser(
            'adm', 'adm@cianet.ind.br', '123'
        )
        self.c = Client()
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
            offline_mode=True,
        )
        nic = NIC.objects.create(server=server, ipv4='127.0.0.1')
        unicastin = UnicastInput.objects.create(
            server=server,
            interface=nic,
            port=30000,
            protocol='udp',
        )
        service = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )
        internal = UniqueIP.create(sink=service)
        self.ipout = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        self.channel = Channel.objects.create(
            number=51,
            name='Discovery Channel',
            description='Cool tv channel',
            channelid='DIS',
            image='',
            enabled=True,
            source=self.ipout,
        )
        storage = Storage.objects.create(
            server=server
        )

        StreamRecorder.objects.create(
            server=server,
            rotate=60,
            sink=internal,
            nic_sink=nic,
            keep_time=168,
            channel=self.channel,
            storage=storage
        )

    def tearDown(self):
        Server = apps.get_model('device', 'Server')
        Server.objects.all().delete()

    def test_logo_thumb(self):
        """Teste para analizar o upload de log e o teste da criação de thumbnail
        """
        Channel = apps.get_model('tv', 'Channel')
        self.c.login(username='adm', password='123')
        with open('tv/fixtures/test_files/a.png', 'r') as imglogo:
            resp = self.c.post('/tv/administracao/tv/channel/add/', {
                'number': 12,
                'name': 'Canal de teste',
                'description': 'Lorem Ipsulum',
                'channelid': 'TES',
                'image': imglogo,
                'buffer_size': 500,
                'enable': True,
                'source': self.ipout.id
            })
            # Garante que foi criado o thumb
            self.assertEqual(302, resp.status_code)
            # Verifica se existe o log e o thumb
            # import ipdb
            # ipdb.set_trace()
            ch = Channel.objects.get(number=12)
            self.assertNotEqual(ch.thumb.name, '')
            self.assertNotEqual(ch.image.name, '')
            # Esperado {MEDIA_ROOT}/tv/channel/image/thumb/{pk}.png
            MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
            thumbfile = '%s/tv/channel/image/thumb/%d.png' % (MEDIA_ROOT, ch.pk)
            imagefile = '%s/tv/channel/image/original/%d.png' % (MEDIA_ROOT, ch.pk)
            self.assertTrue(os.path.exists(thumbfile))
            self.assertTrue(os.path.exists(imagefile))


class APITest(TestCase):
    """
    Test API for ERP
    """

    def setUp(self):
        import getpass
        Server = apps.get_model('device', 'Server')
        NIC = apps.get_model('device', 'NIC')
        UnicastInput = apps.get_model('device', 'UnicastInput')
        DemuxedService = apps.get_model('device', 'DemuxedService')
        UniqueIP = apps.get_model('device', 'UniqueIP')
        MulticastOutput = apps.get_model('device', 'MulticastOutput')
        Channel = apps.get_model('tv', 'Channel')
        super(APITest, self).setUp()
        self.c = Client()
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
            offline_mode=True,
        )
        nic = NIC.objects.create(server=server, ipv4='127.0.0.1')
        unicastin = UnicastInput.objects.create(
            server=server,
            interface=nic,
            port=30000,
            protocol='udp',
        )
        service = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )
        internal = UniqueIP.create(sink=service)
        ipout1 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.2',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        ipout2 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        ipout3 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.4',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        self.channel1 = Channel.objects.create(
            number=51,
            name='Discovery Channel',
            description='Cool tv channel',
            channelid='DIS',
            image='',
            enabled=True,
            source=ipout1,
        )
        self.channel2 = Channel.objects.create(
            number=13,
            name='Globo',
            description='Rede globo de televisão',
            channelid='GLB',
            image='',
            enabled=True,
            source=ipout2,
        )
        self.channel3 = Channel.objects.create(
            number=14,
            name='Test 3',
            description='Rede Test 3',
            channelid='GLB',
            image='',
            enabled=True,
            source=ipout3,
        )

    def tearDown(self):
        Server = apps.get_model('device', 'Server')
        Server.objects.all().delete()

    def test_created(self):
        Channel = apps.get_model('tv', 'Channel')
        channels = Channel.objects.all()
        self.assertEqual(3, channels.count())

    def test_call_schema(self):
        c = Client()
        # api_dispatch_list,api_get_schema,api_get_multiple,api_dispatch_detail
        # e = resolve('/tv/api/epg/v1/channel/')
        # print('epg=%s' % e)
        # t = resolve('/tv/api/tv/v1/channel/')
        # print('tv=%s' % t)
        urlschema = reverse(
            'tv_v1:api_get_schema',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'}
        )
        self.assertEqual(urlschema, '/tv/api/tv/v1/channel/schema/')
        response = c.get(urlschema)
        # Unautenticated
        self.assertEqual(response.status_code, 401)
        # self.assertContains(response, 'channelid', 1, 200)

    def test_list_channels(self):
        # Define auto_create and execute again
        clientmodels.SetTopBox.options.auto_create = True
        clientmodels.SetTopBox.options.auto_add_channel = True
        clientmodels.SetTopBox.options.use_mac_as_serial = True
        clientmodels.SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        url = reverse(
            'tv_v1:api_dispatch_list',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'}
        )
        self.assertEqual(url, '/tv/api/tv/v1/channel/')
        response = self.c.get(url)
        import simplejson as json
        # Objeto JSON
        jcanal = json.loads(response.content)
        self.failUnlessEqual(
            jcanal['meta']['total_count'], 3, 'Deveria haver 3 canais'
        )
        obj = jcanal['objects']
        self.assertEqual(obj[0]['previous'], None)
        self.assertEqual(obj[0]['resource_uri'], obj[1]['previous'])
        self.assertEqual(obj[1]['resource_uri'], obj[2]['previous'])
        self.assertEqual(obj[0]['next'], obj[1]['resource_uri'])
        self.assertEqual(obj[1]['next'], obj[2]['resource_uri'])
        self.assertEqual(obj[2]['next'], None)

    def test_channel_v2(self):
        import simplejson as json
        decoder = json.JSONDecoder()
        c = Client()
        url_all = reverse(
            'tv_v2:api_dispatch_list',
            kwargs={'api_name': 'v2', 'resource_name': 'channel'}
        )
        self.assertEqual('/tv/api/tv/v2/channel/', url_all)
        response = c.get(url_all)
        jcanal = decoder.decode(response.content)
        obj = jcanal['objects']
        self.assertEqual(obj[0]['previous'], None)
        self.assertEqual(obj[0]['resource_uri'], obj[1]['previous'])
        self.assertEqual(obj[1]['resource_uri'], obj[2]['previous'])
        self.assertEqual(obj[0]['next'], obj[1]['resource_uri'])
        self.assertEqual(obj[1]['next'], obj[2]['resource_uri'])
        self.assertEqual(obj[2]['next'], None)
        self.assertEqual(response.status_code, 200)
        chid = self.channel2.id
        url = reverse(
            'tv_v2:api_dispatch_detail',
            kwargs={'pk': chid, 'api_name': 'v2', 'resource_name': 'channel'}
        )
        log.debug('URL=%s', url)
        self.assertEqual(url, '/tv/api/tv/v2/channel/%d/' % (chid))
        response = c.get(url)
        log.debug('Resposta=%s', response.content)
        self.assertEqual(response.status_code, 200)
        # Objeto JSON
        jcanal = decoder.decode(response.content)
        self.failUnlessEqual(jcanal['description'], 'Rede globo de televisão')
        self.failUnlessEqual(jcanal['name'], 'Globo')

    def test_auth_v2(self):
        import simplejson as json
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
        Channel = apps.get_model('tv', 'Channel')
        clientmodels.SetTopBox.options.auto_create = False
        clientmodels.SetTopBox.options.auto_add_channel = False
        clientmodels.SetTopBox.options.use_mac_as_serial = True
        clientmodels.SetTopBox.options.auto_enable_recorder_access = True
        decoder = json.JSONDecoder()
        url_all = reverse(
            'tv_v2:api_dispatch_list',
            kwargs={'api_name': 'v2', 'resource_name': 'channel'}
        )
        self.assertEqual('/tv/api/tv/v2/channel/', url_all)
        response = self.c.get(url_all)
        jcanal = decoder.decode(response.content)
        self.assertEqual(3, jcanal['meta']['total_count'])
        url_auth = reverse(
            'tv_v2:api_dispatch_list',
            kwargs={'api_name': 'v2', 'resource_name': 'userchannel'}
        )
        self.assertEqual('/tv/api/tv/v2/userchannel/', url_auth)
        response = self.c.get(url_auth)
        self.assertEqual(401, response.status_code)
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        # Cria o STB
        stb = SetTopBox.objects.create(
            serial_number='01:02:03:04:05:06',
            mac='01:02:03:04:05:06')
        # self.assertTrue(stb)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        # get api_key
        jobj = decoder.decode(response.content)
        api_key = jobj['api_key']
        # Primeira consulta (Lista vazia)
        response = self.c.get(url_auth + '?api_key=' + api_key)
        self.assertEqual(200, response.status_code)
        # log.debug('Conteudo:%s', response.content)
        canais = Channel.objects.all()
        log.debug('STB-CH=%s', SetTopBoxChannel.objects.all())
        SetTopBoxChannel.objects.create(
            settopbox=stb, channel=canais[1], recorder=False
        )
        response = self.c.get(url_auth + '?api_key=' + api_key)
        self.assertEqual(200, response.status_code)
        # log.debug('Conteudo:%s', response.content)
        self.assertContains(response, canais[1].channelid)
        SetTopBoxChannel.objects.create(
            settopbox=stb, channel=canais[0], recorder=True
        )
        response = self.c.get(url_auth + '?api_key=' + api_key)
        self.assertEqual(200, response.status_code)
        log.debug('Conteudo:%s', response.content)
        self.assertContains(response, canais[0].channelid)
        SetTopBoxChannel.objects.create(
            settopbox=stb, channel=canais[2], recorder=True
        )
        response = self.c.get(url_auth + '?api_key=' + api_key)
        self.assertEqual(200, response.status_code)
        log.debug('Conteudo:%s', response.content)
        self.assertContains(response, canais[2].channelid)
        # Cria um novo STB
        stb1 = SetTopBox.objects.create(
            serial_number='01:02:03:04:05:07',
            mac='01:02:03:04:05:07')
        # Sair do sistema
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        # login com novo STB
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:07'})
        self.assertEqual(200, response.status_code)
        # get api_key
        jobj = decoder.decode(response.content)
        api_key = jobj['api_key']
        # Primeira consulta (Lista vazia)
        response = self.c.get(url_auth + '?api_key=' + api_key)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '"total_count": 0')
        SetTopBoxChannel.objects.create(
            settopbox=stb1, channel=canais[2], recorder=True
        )
        response = self.c.get(url_auth + '?api_key=' + api_key)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '"total_count": 1')
