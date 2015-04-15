# -*- encoding:utf-8 -*-
from __future__ import unicode_literals, absolute_import
import simplejson as json
import logging
import simplejson

from django.apps import apps
from django.core.urlresolvers import reverse, resolve
from django.conf import settings
from django.test.utils import override_settings
from django.test import TestCase
from django.test import client
from django.utils import timezone


log = logging.getLogger('unittest')


# curl --dump-header - -H "Content-Type: application/json" -X POST --data \
# '{"serial_number": "lala"}' http://127.0.0.1:8000/tv/api/client/v1/settopbox/
# HTTP/1.0 201 CREATED
# Date: Fri, 10 Aug 2012 21:23:43 GMT
# Server: WSGIServer/0.1 Python/2.7.3
# Content-Type: text/html; charset=utf-8
# Location: http://127.0.0.1:8000/tv/api/client/v1/settopbox/1/


# curl --dump-header - -H "Content-Type: application/json" -X POST --data \
# '{"objects": [{"serial_number": "abc"}, {"serial_number": "efg"}, \
# {"serial_number": "hij"}, {"serial_number": "aeh"}]}' \
# http://127.0.0.1:8000/tv/api/client/v1/settopbox/


class APITest(TestCase):
    '''
    Testes de manipulação de settopbox e associação de canais através da api.
    http://10.1.1.200/projects/iptv/wiki/Wiki
    Seja client.SetTopBox = stb e tv.Channel = ch
**Listagem de stb
**Criação de stb
**Retorna erro ao tentar criar um stb com serial_number duplicado
**Modificação de stb
***Parcial
***Total
***Em lote
**Remoção de stb
**Cria associação de stb com ch
**Retorna erro ao criar uma associação duplicada
**Listar associação ch-stb
**Listar stb filtrado por ch
**Remover associação de ch-stb
**Removendo stb é removido a associação
**Removendo ch é removido a associação
**Autenticação para acesso
***Login e senha
***Token
**Permissão na de execução do usuário (ERP)
    '''

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            'erp', 'erp@cianet.ind.br', '123'
        )
        self.user.save()

    def test_SetTopBox(self):
        from django.contrib.auth.models import Permission
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = False
        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        c = client.Client()
        # Buscando o schema
        urlschema = reverse(
            'client:api_get_schema', kwargs={'resource_name': 'settopbox', 'api_name': 'v1'}
        )
        # self.encoded_creds = "Basic " + "demo:demo".encode("base64")
        c.login(username='erp', password='123')
        response = c.get(urlschema)
        jschema = json.loads(response.content)
        self.assertEqual('string', jschema['fields']['serial_number']['type'])
        # Buscando lista
        url = reverse(
            'client:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'},
        )
        response = c.get(url)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        # Try to create new SetTopBox using post on api,
        # but need to logged in
        response = c.post(
            url, data=json.dumps({
                'serial_number': 'lalala', 'mac': '00:00:00:00:00:00'
            }),
            content_type='application/json'
        )
        self.assertEqual(401, response.status_code)
        # Create new user and do login to into middlewer
        # user = User.objects.create_user('erp', 'erp@cianet.ind.br', '123')
        user = self.user
        urllogin = reverse('sys_login')
        response = c.post(urllogin, {'username': 'erp', 'password': '123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        # Try again and responds with no permission
        response = c.post(
            url, data=json.dumps({
                'serial_number': 'lalala', 'mac': '00:00:00:00:00:00'
            }),
            content_type='application/json'
        )
        self.assertEqual(401, response.status_code)
        # Create permission to create stb
        perm_add_stb = Permission.objects.get(codename='add_settopbox')
        user.user_permissions.add(perm_add_stb)
        user.save()
        # Create new SetTopBox using post
        response = c.post(
            url, data=json.dumps({
                'serial_number': 'lalala', 'mac': '00:00:00:00:00:00'
            }),
            content_type='application/json'
        )
        self.assertEqual(201, response.status_code)
        stbs = SetTopBox.objects.all()
        self.assertEqual(1, stbs.count())
        self.assertEqual('lalala', stbs[0].serial_number)
        # Try to add new stb with existing serial_number
        response = c.post(
            url, data=json.dumps({
                'serial_number': 'lalala', 'mac': '00:00:00:00:00:11'
            }),
            content_type='application/json'
        )
        #import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, 400)
        # Error message on duplicated serial_number
        self.assertContains(response, 'serial_number', status_code=400)
        # Delete one stb
        urldelete = reverse('client:api_dispatch_detail', kwargs={
            'resource_name': 'settopbox', 'api_name': 'v1', 'pk': stbs[0].pk
        })
        response = c.delete(urldelete)
        # Deve retornar 401 UNAUTHORIZED
        self.assertEqual(response.status_code, 401)
        # Add authorization to DELETE
        perm_delete_stb = Permission.objects.get(codename='delete_settopbox')
        self.user.user_permissions.add(perm_delete_stb)
        response = c.delete(urldelete)
        self.assertEqual(204, response.status_code)
        stbs = SetTopBox.objects.all()
        self.assertEqual(0, len(stbs))
        # Try to edit one settop box

    def test_PATCH(self):
        from django.contrib.auth.models import Permission
        SetTopBox = apps.get_model('client', 'SetTopBox')

        c = client.Client()
        c.login(username='erp', password='123')
        # urllogin = reverse('sys_login')
        # response = c.post(urllogin, {'username': 'erp', 'password': '123'},
        #    follow=True)
        # self.assertEqual(response.status_code, 200)
        # Buscando lista
        url = reverse(
            'client:api_dispatch_list', kwargs={'resource_name': 'settopbox', 'api_name': 'v1'},
        )
        # Create multiples (4) stbs in one call
        objects = {'objects': [
            {'serial_number': 'abc', 'mac': '00:00:00:00:00:00'},
            {'serial_number': 'efg', 'mac': '00:00:00:00:00:01'},
            {'serial_number': 'hij', 'mac': '00:00:00:00:00:02'},
            {'serial_number': 'aeh', 'mac': '00:00:00:00:00:03'}
        ]}
        serialized = json.dumps(objects)
        p = self.user.user_permissions
        p.add(Permission.objects.get(codename='add_settopbox'))
        p.add(Permission.objects.get(codename='change_settopbox'))
        p.add(Permission.objects.get(codename='delete_settopbox'))
        # self.user.save()
        response = c.patch(url, data=serialized, content_type='application/json')
        self.assertEqual(response.status_code, 202)
        stbs = SetTopBox.objects.all()
        self.assertEqual(4, stbs.count())

    def test_missing_mac(self):
        c = client.Client()
        c.login(username='erp', password='123')
        url = reverse(
            'client:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'},
        )
        response = c.post(url, data=json.dumps({
            'serial_number': 'lalala'}
        ), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        log.debug('Resposta=%s', response.content)
        self.assertContains(response, 'mac', 1, 400)

    def test_invalid_mac(self):
        from django.contrib.auth.models import Permission
        c = client.Client()
        c.login(username='erp', password='123')
        p = self.user.user_permissions
        p.add(Permission.objects.get(codename='add_settopbox'))
        p.add(Permission.objects.get(codename='change_settopbox'))
        p.add(Permission.objects.get(codename='delete_settopbox'))
        url = reverse(
            'client:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'},
        )
        # Invalid
        response = c.post(url, data=json.dumps({
            'serial_number': 'a1', 'mac': 'la'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'mac', 1, 400)
        # Invalid
        response = c.post(url, data=json.dumps({
            'serial_number': 'a2', 'mac': '5c:f9:dd:ee:21:d'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'mac', 1, 400)
        # Invalid
        response = c.post(url, data=json.dumps({
            'serial_number': 'a3', 'mac': '5c:f9:dd:ee:21:dZ'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'mac', 1, 400)
        # Valid
        response = c.post(url, data=json.dumps({
            'serial_number': 'a4', 'mac': '5c:f9:dd:ee:21:dA'
        }), content_type='application/json')
        log.debug('Resposta=%s', response.content)
        self.assertEqual(response.status_code, 201)
        self.assertContains(response, 'mac', 1, 201)


@override_settings(DVBLAST_COMMAND=settings.DVBLAST_DUMMY)
@override_settings(DVBLASTCTL_COMMAND=settings.DVBLASTCTL_DUMMY)
@override_settings(MULTICAT_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(CHANNEL_RECORD_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(CHANNEL_RECORD_PLAY_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(MULTICATCTL_COMMAND=settings.MULTICATCTL_DUMMY)
@override_settings(VLC_COMMAND=settings.VLC_DUMMY)
class SetTopBoxChannelTest(TestCase):

    def setUp(self):
        # import getpass
        from django.contrib.auth.models import User, Permission
        Server = apps.get_model('device', 'Server')
        NIC = apps.get_model('device', 'Nic')
        UnicastInput = apps.get_model('device', 'UnicastInput')
        DemuxedService = apps.get_model('device', 'DemuxedService')
        UniqueIP = apps.get_model('device', 'UniqueIP')
        MulticastOutput = apps.get_model('device', 'MulticastOutput')
        Channel = apps.get_model('tv', 'Channel')
        Storage = apps.get_model('device', 'Storage')
        StreamRecorder = apps.get_model('device', 'StreamRecorder')

        super(SetTopBoxChannelTest, self).setUp()
        self.c = client.Client()
        self.user = User.objects.create_user('erp', 'erp@cianet.ind.br', '123')
        self.user.is_staff = True
        self.user.save()
        urllogin = reverse('sys_login')
        response = self.c.post(urllogin, {'username': 'erp', 'password': '123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        perm_add_relation = Permission.objects.get(
            codename='add_settopboxchannel')
        self.user.user_permissions.add(perm_add_relation)
        perm_delete_relation = Permission.objects.get(
            codename='delete_settopboxchannel')
        self.user.user_permissions.add(perm_delete_relation)
        server, created = Server.objects.get_or_create(
            host='127.0.0.1', offline_mode=True
        )
        server.name = 'local'
        server.ssh_port = 22
        server.username = 'nginx'
        server.rsakey = '~/.ssh/id_rsa'
        server.offline_mode = True
        server.status = False
        server.save()
        nic, created = NIC.objects.get_or_create(
            server=server, ipv4='127.0.0.1'
        )
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
        self.ipout4 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.5',
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
            channelid='RIC',
            image='',
            enabled=True,
            source=ipout3,
        )
        storage = Storage.objects.create(
            folder='/tmp/test_record',
            server=server
        )
        self.rec1 = StreamRecorder.objects.create(
            channel=self.channel1,
            rotate=5,
            storage=storage,
            keep_time=10,
            nic_sink=nic,
            server=server
        )
        self.rec2 = StreamRecorder.objects.create(
            channel=self.channel2,
            rotate=5,
            storage=storage,
            keep_time=20,
            nic_sink=nic,
            server=server
        )
        self.rec3 = StreamRecorder.objects.create(
            channel=self.channel3,
            rotate=5,
            storage=storage,
            keep_time=48,
            nic_sink=nic,
            server=server
        )
        self.rec1.status = True
        self.rec2.status = True
        self.rec3.status = True
        z = timezone.utc
        self.rec1.start_time = timezone.datetime(2013, 2, 13, 17, 13, 59, 0, z)
        self.rec2.start_time = timezone.datetime(2013, 3, 5, 17, 13, 59, 0, z)
        self.rec3.start_time = timezone.datetime(2013, 3, 1, 17, 13, 59, 0, z)
        self.rec1.save()
        self.rec2.save()
        self.rec3.save()

    def test_channel_stb(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        Channel = apps.get_model('tv', 'Channel')

        self.assertEqual(Channel.objects.all().count(), 3)
        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = True
        self.assertEqual(SetTopBox.options.auto_add_channel, False)
        stb1 = SetTopBox.objects.create(
            serial_number='lalala', mac='00:00:00:00:00:00'
        )
        stb2 = SetTopBox.objects.create(
            serial_number='lelele', mac='00:00:00:00:00:01'
        )
        SetTopBox.objects.create(
            serial_number='lilili', mac='00:00:00:00:00:02'
        )
        SetTopBox.objects.create(
            serial_number='lololo', mac='00:00:00:00:00:03'
        )
        SetTopBox.objects.create(
            serial_number='lululu', mac='00:00:00:00:00:04'
        )
        self.assertEqual(SetTopBox.objects.all().count(), 5)
        # Get channel list
        urlchannels = reverse(
            'tv_v1:api_dispatch_list',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'}
        )
        response = self.c.get(urlchannels)
        self.assertEqual(200, response.status_code)
        jobj = json.loads(response.content)
        # Ensure there is 3 channels in list
        self.assertEqual(3, jobj['meta']['total_count'])

        urllogin = reverse('sys_login')
        response = self.c.post(
            urllogin,
            {'username': 'erp', 'password': '123'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Get stb list
        urlstb = reverse(
            'client:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'}
        )
        response = self.c.get(urlstb)
        jobj = json.loads(response.content)
        # Ensure there is 5 SetTopBox in list
        self.assertEqual(5, jobj['meta']['total_count'])
        # Add relation bethen stb and 2 channels
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxchannel', 'api_name': 'v1'})
        response = self.c.post(
            urlrelation, data=json.dumps({
                'settopbox': '/tv/api/client/v1/settopbox/%s/' % (stb1.pk),
                'channel': '/tv/api/tv/v1/channel/%s/' % (self.channel2.pk),
                'recorder': True}),
            content_type='application/json'
        )
        self.assertEqual(
            response.status_code, 201,
            'Content:%s' % response.content
        )
        response = self.c.post(urlrelation, data=json.dumps({
            'settopbox': '/tv/api/client/v1/settopbox/%s/' % (stb2.pk),
            'channel': '/tv/api/tv/v1/channel/%s/' % (self.channel2.pk),
            'recorder': True}),
            content_type='application/json')
        # Retorna erro ao criar uma associação duplicada
        response = self.c.post(
            urlrelation, data=json.dumps({
                'settopbox': '/tv/api/client/v1/settopbox/%s/' % (stb1.pk),
                'channel': '/tv/api/tv/v1/channel/%s/' % (self.channel2.pk),
                'recorder': True}
            ),
            content_type='application/json'
        )
        self.assertEqual(400, response.status_code)
        # Respond properly error message on duplicated
        self.assertContains(
            response, 'settopbox_id', status_code=400
        )

    def test_settopbox_options(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = True
        self.assertEqual(
            SetTopBox.options.auto_add_channel, False,
            'Default value not working'
        )
        self.assertEqual(
            SetTopBox.options.use_mac_as_serial, True,
            'Default value not working'
        )

    def test_auth_get(self):
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(response.status_code, 200)
        response = self.c.get(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(401, response.status_code)

    def test_settopbox_autologin(self):
        # Define auto_create and execute again
        from django.contrib.auth.models import User
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
        Channel = apps.get_model('tv', 'Channel')

        SetTopBox.options.auto_create = False
        SetTopBox.options.auto_add_channel = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(403, response.status_code)
        # Define auto_create and execute again
        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        # Busca o ususário criado para o stb
        user = User.objects.get(
            username=settings.STB_USER_PREFIX + '01:02:03:04:05:06')
        # Verifica se existe a relação criado nos 3 canais
        # Busca o stb
        stb = SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        self.assertEqual(user, stb.get_user())
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        # Número de stb-channel
        self.assertEqual(3, stb_ch.count())
        # Remove o canal Globo
        self.channel2.delete()
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        self.assertEqual(2, stb_ch.count())
        # Create new channel
        ch = Channel.objects.create(
            number=18,
            name='Globo 2',
            description='Rede globo 2 de televisão',
            channelid='GLB',
            image='',
            enabled=True,
            source=self.ipout4
        )
        stb_ch = SetTopBoxChannel.objects.filter(
            settopbox=stb, channel=ch
        )
        self.assertEqual(1, stb_ch.count())
        response = self.c.post(
            auth_login, data={'mac': '01:02:03:04:05:00', 'sn': 123456}
        )
        self.assertEqual(200, response.status_code)
        stb = SetTopBox.objects.get(serial_number=123456)
        # Busca o ususário criado para o stb
        user = User.objects.get(
            username=settings.STB_USER_PREFIX + '123456'
        )
        self.assertEqual(user, stb.get_user())

    def test_case_insensitive_mac_sn(self):
        # Define auto_create and execute again
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = False
        SetTopBox.options.auto_add_channel = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        # Define auto_create and execute again
        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        # Now disable auto_create
        SetTopBox.options.auto_create = False
        SetTopBox.options.auto_add_channel = False
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:00'})
        self.assertEqual(403, response.status_code)
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        response = self.c.post(
            auth_login, data={
                'mac': '01:02:03:04:05:06', 'sn': '01:02:03:04:05:06'
            }
        )
        self.assertEqual(200, response.status_code)
        response = self.c.post(
            auth_login, data={
                'MAC': '01:02:03:04:05:06', 'SN': '01:02:03:04:05:06'
            }
        )
        self.assertEqual(200, response.status_code)

    def test_get_channels_from_stb(self):
        # Define auto_create and execute again
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
        Channel = apps.get_model('tv', 'Channel')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={
            'sn': '01:02:03:04:05:06', 'MAC': '01:02:03:04:05:06'
        })
        self.assertEqual(200, response.status_code)
        stb = SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        tvchannels = Channel.objects.all()
        try:
            channels = stb.get_channels()
        except Exception:
            self.assertFalse(
                True,
                'O metodo SetTopBox.get_channels() deveria existir')
        self.assertItemsEqual(channels, tvchannels)
        # Remove uma relação
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        stb_ch[1].delete()
        channels = stb.get_channels()
        self.assertEqual(2, channels.count())
        url_channel = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(2, jobj['meta']['total_count'])

    def test_stb_api_tv(self):
        # Define auto_create and execute again
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={
            'SN': '01:02:03:04:05:06', 'MAC': '01:02:03:04:05:06'
        })
        self.assertEqual(200, response.status_code)
        stb = SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        self.assertEqual(stb.serial_number, '01:02:03:04:05:06')
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        self.assertEqual(3, stb_ch.count())
        url_channel = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        # Get list of channels
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])
        # Remove one relation
        stb_ch[2].delete()
        # Check removed element
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        self.assertEqual(2, stb_ch.count())
        # Get list of channels again
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        # Ensure has 2 channels on response
        self.assertEqual(2, jobj['meta']['total_count'])
        # Test Anonimous
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.get(url_channel)
        self.assertEqual(401, response.status_code)

    def test_list_records(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
        StreamRecorder = apps.get_model('device', 'StreamRecorder')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        # Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        # Call tvod_list
        url_tvod = reverse('device.views.tvod_list')
        self.assertEqual(url_tvod, '/tv/device/tvod_list/')
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        # Do login
        response = self.c.post(auth_login, data={
            'SN': '01:02:03:04:05:06', 'MAC': '01:02:03:04:05:06'
        })
        self.assertEqual(200, response.status_code)
        # Get list of records
        recs = StreamRecorder.objects.all()
        self.assertEqual(3, recs.count())
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        # Get STB
        stb = SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        # Get STB-ch relation
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        # Enable record access to 1 channel
        rec = stb_ch[1]
        rec.recorder = True
        rec.save()
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        # Call tvod_list
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(1, jobj['meta']['total_count'])
        # Enable record access to second channel
        stb_ch = SetTopBoxChannel.objects.filter(settopbox=stb)
        stb_ch.update(recorder=True)
        # Call tvod_list
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])

    def test_play_record(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        # Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        # Try play recorder ch=13, 14, 51
        # channel_number=None, command=None, seek=0
        url_play = reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'play',
            'seek': 20})
        self.assertEqual('/tv/device/tvod/13/play/20', url_play)
        response = self.c.get(url_play)
        self.assertEqual(401, response.status_code)
        # Do login
        response = self.c.post(auth_login, data={
            'sn': 'lala', 'MAC': '01:02:03:04:05:06'
        })
        self.assertEqual(200, response.status_code)
        # No channel
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 15,
            'command': 'play',
            'seek': 20
        }))
        self.assertEqual(404, response.status_code)
        # No seek avaliable
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'play',
            'seek': 200000
        }))
        self.assertEqual(404, response.status_code)
        # All OK
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'play',
            'seek': 200
        }))
        self.assertEqual(200, response.status_code)
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'stop',
            'seek': 20
        }))
        self.assertEqual(409, response.status_code)

    def test_list_disable_channel(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        # Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        url_channel = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        # Get list of channels
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])
        self.channel2.enabled = False
        self.channel2.save()
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(2, jobj['meta']['total_count'])

    def test_patch_stb_channel(self):
        from django.contrib.auth.models import Permission
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = False
        SetTopBox.options.auto_enable_recorder_access = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        # Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={
            'sn': 'a1', 'MAC': '01:02:03:04:05:06'
        })
        self.assertEqual(200, response.status_code)
        url_userchannel = reverse('tv_v2:api_dispatch_list', kwargs={
            'resource_name': 'userchannel', 'api_name': 'v2'})
        self.assertEqual('/tv/api/tv/v2/userchannel/', url_userchannel)
        # Get list of channels
        response = self.c.get(url_userchannel)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        self.channel2.enabled = False
        self.channel2.save()
        response = self.c.get(url_userchannel)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        # Agora tem 3 canais sendo 1 desabilitado
        urllogin = reverse('sys_login')
        response = self.c.post(urllogin, {'username': 'erp', 'password': '123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        perm_add_relation = Permission.objects.get(
            codename='add_settopboxchannel')
        self.user.user_permissions.add(perm_add_relation)
        perm_delete_relation = Permission.objects.get(
            codename='delete_settopboxchannel')
        self.user.user_permissions.add(perm_delete_relation)
        url_channel = reverse('tv_v2:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v2'
        })
        response = self.c.get(url_channel)
        log.debug('All=%s', response.content)
        response = self.c.get(url_userchannel)
        log.debug('User=%s', response.content)

    def test_api_key_channel(self):
        from tastypie.models import ApiKey
        from django.contrib.auth.models import User
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        # Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={
            'sn': 'lala', 'MAC': '01:02:03:04:05:06'
        })
        self.assertEqual(200, response.status_code)
        user = User.objects.get(
            username=settings.STB_USER_PREFIX + 'lala'
        )
        self.assertIsNotNone(user)
        api_key = ApiKey.objects.get(user=user)
        self.assertIsNotNone(api_key)
        self.assertContains(response, 'api_key')
        jobj = json.loads(response.content)
        api_key = jobj.get('api_key')
        self.assertIsNotNone(api_key)
        # Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        url_channel = reverse(
            'tv_v1:api_dispatch_list',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'}
        )
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        # Get empty list (Anonymous)
        response = self.c.get(url_channel)
        self.assertEqual(401, response.status_code)
        # Get list of channels
        response = self.c.get(url_channel + '?api_key=%s' % api_key)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])


class TestRequests(TestCase):

    def setUp(self):
        self.c = client.Client()

    def test_call_login(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxConfig = apps.get_model('client', 'SetTopBoxConfig')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.post(auth_login, data={
            'sn': 'lala', 'MAC': '01:02:03:04:05:06'
        })
        self.assertContains(response, 'api_key')
        key = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key)

        # Create new STBconfig
        url_config = reverse(
            'client:api_dispatch_list',
            kwargs={'resource_name': 'settopboxconfig', 'api_name': 'v1'}
        )
        self.assertEqual('/tv/api/client/v1/settopboxconfig/', url_config)

        # Get STBconfig
        response = self.c.get(url_config)
        self.assertEqual(response.status_code, 200)
        jobj = simplejson.loads(response.content)
        self.assertEqual(jobj['meta']['total_count'], 3)

        # Create a config
        data = simplejson.dumps(
            {"key": "VOLUME_LEVEL", "value": "0.5", "value_type": "Number"}
        )
        response = self.c.post(
            url_config, data=data, content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.has_header('location'))
        # load stb config
        response = self.c.get(url_config)
        self.assertEqual(response.status_code, 200)
        jobj = simplejson.loads(response.content)
        self.assertEqual(jobj['meta']['total_count'], 4)
        # login on new STB
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:07'})
        self.assertContains(response, 'api_key')
        key1 = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key1)
        data = simplejson.dumps(
            {"key": "VOLUME_LEVEL", "value": "0.3", "value_type": "Number"}
        )
        response = self.c.post(
            url_config, data=data, content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.has_header('location'))
        response = self.c.get(url_config)
        self.assertEqual(response.status_code, 200)
        jobj = simplejson.loads(response.content)
        log.debug(jobj)
        self.assertEqual(jobj['meta']['total_count'], 4)
        # Change volume value
        url_vol = reverse('client:api_dispatch_detail', kwargs={
            'resource_name': 'settopboxconfig', 'api_name': 'v1', 'pk': 5})
        self.assertEqual('/tv/api/client/v1/settopboxconfig/5/', url_vol)
        response = self.c.get('/tv/api/client/v1/settopboxconfig/')
        self.assertEqual(response.status_code, 200)
        data = simplejson.dumps({"value": "0.2"})
        response = self.c.put(
            url_vol, data=data, content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        conf = SetTopBoxConfig.objects.get(id=5)
        self.assertEqual('0.2', conf.value)
        response = self.c.get(auth_logoff)
        self.assertEqual(response.status_code, 200)
        response = self.c.get(url_vol + '?api_key=%s' % key)
        # log.debug('status_code=%s, content=%s', response.status_code,
        #    response.content)
        self.assertEqual(response.status_code, 400)


class TestDefaultConfig(TestCase):

    def setUp(self):
        self.c = client.Client()

    def test_call_login(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        SetTopBox.default.password = '1234'
        SetTopBox.default.recorder = True
        SetTopBox.default.parental = '18'
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertContains(response, 'api_key')
        key = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key)
        # Create new STBconfig
        url_config = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxconfig', 'api_name': 'v1'})
        self.assertEqual('/tv/api/client/v1/settopboxconfig/', url_config)
        response = self.c.get(url_config)
        self.assertContains(response, 'global.PASSWORD')
        self.assertContains(response, '1234')
        self.assertContains(response, 'app/tv.PARENTAL_CONTROL')
        self.assertContains(response, '"value": "18"')
        self.assertContains(response, '"value": "enable"')
        SetTopBox.default.password = '2222'
        SetTopBox.default.recorder = False
        SetTopBox.default.parental = '-1'
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:07'})
        self.assertContains(response, 'api_key')
        key = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key)
        response = self.c.get(url_config)
        self.assertContains(response, 'global.PASSWORD')
        self.assertContains(response, '2222')
        self.assertContains(response, 'app/tv.PARENTAL_CONTROL')
        self.assertContains(response, '"value": "-1"')
        self.assertContains(response, '"value": "disabled"')
        response = self.c.get(auth_logoff)
        self.assertEqual(response.status_code, 200)


class SetTopBoxProgramScheduleTest(TestCase):

    def setUp(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        Server = apps.get_model('device', 'Server')
        NIC = apps.get_model('device', 'NIC')
        UnicastInput = apps.get_model('device', 'UnicastInput')
        DemuxedService = apps.get_model('device', 'DemuxedService')
        UniqueIP = apps.get_model('device', 'UniqueIP')
        MulticastOutput = apps.get_model('device', 'MulticastOutput')
        Channel = apps.get_model('tv', 'Channel')

        self.c1 = client.Client()
        self.c2 = client.Client()
        self.c3 = client.Client()
        self.auth_login = reverse('client_auth')
        self.auth_logoff = reverse('client_logoff')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True

        server, created = Server.objects.get_or_create(
            host='127.0.0.1', offline_mode=True
        )
        server.name = 'local'
        server.ssh_port = 22
        server.username = 'nginx'
        server.rsakey = '~/.ssh/id_rsa'
        server.offline_mode = True
        server.status = False
        server.save()

        nic, created = NIC.objects.get_or_create(server=server, ipv4='127.0.0.1')

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

    def test_program_schedule(self):
        """
        Realiza login com SetTopBox 1 e SetTopBox 2
        """
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxProgramSchedule = apps.get_model('client', 'SetTopBoxProgramSchedule')

        response = self.c1.post(
            self.auth_login, data={'MAC': '01:02:03:04:05:06'}
        )
        self.assertEqual(200, response.status_code)

        response = self.c2.post(
            self.auth_login, data={'MAC': '01:02:03:04:05:07'}
        )
        self.assertEqual(200, response.status_code)

        stb1 = SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        stb2 = SetTopBox.objects.get(serial_number='01:02:03:04:05:07')

        # tz = timezone.utc
        # post_date = datetime(2014, 4, 9, 18,53,13,0,tz)

        """
        Realiza um agendamento no SetTopBox 1 e
        dois agendamentos no SetTopBox 2
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c1.post(urlrelation, data=json.dumps({
            'settopbox': '1',
            'channel': '51',
            'url': '/tv/api/1',
            'message': 'O programa Y foi agendado com sucesso!',
            'schedule_date': '1388657410'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.post(urlrelation, data=json.dumps({
            'settopbox': '1',
            'channel': '13',
            'url': '/tv/api/1',
            'message': 'O programa X foi agendado com sucesso!',
            'schedule_date': '1388657410'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.post(urlrelation, data=json.dumps({
            'settopbox': '1',
            'channel': '13',
            'url': '/tv/api/1',
            'message': 'O programa Z foi agendado com sucesso!',
            'schedule_date': '1388657410'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)

        """
        Valida dados de agendamento no SetTopBox 1 e SetTopBox 2
        """
        ps1 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb1)[0]
        ps2 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)[0]

        self.assertEqual(ps1.message, 'O programa Y foi agendado com sucesso!')
        self.assertEqual(ps1.url, '/tv/api/1')
        # dt = datetime(2014, 4, 9, 18,53,13,0,tz)
        self.assertEqual(ps1.schedule_date, 1388657410)

        self.assertEqual(ps2.message, 'O programa Z foi agendado com sucesso!')
        self.assertEqual(ps2.url, '/tv/api/1')
        # dt = datetime(2014, 4, 9, 18,53,13,0,tz)
        self.assertEqual(ps2.schedule_date, 1388657410)

        ps1 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb1)
        self.assertEqual(ps1.count(), 1)

        """
        Remove agendamento no SetTopBox 1
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c1.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        response = self.c1.delete(jsdata['objects'][0]['resource_uri'])
        self.assertEqual(204, response.status_code)

        """
        Valida remoção do agendamento no SetTopBox 1
        """
        ps1 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb1)
        self.assertEqual(ps1.count(), 0)

        """
        Realiza login com SetTopBox 3
        """
        response = self.c3.post(
            self.auth_login, data={'MAC': '01:02:03:04:05:08'}
        )
        self.assertEqual(200, response.status_code)

        stb3 = SetTopBox.objects.get(serial_number='01:02:03:04:05:08')

        """
        Valida se o SetTopBox 3 não possui agendamentos
        """
        ps3 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb3)
        self.assertEqual(ps3.count(), 0)

        """
        Valida se a remoção do agendamento no SetTopBox 1
        não influenciou no agendamento do SetTopBox 2
        """
        stb2 = SetTopBox.objects.get(serial_number='01:02:03:04:05:07')

        ps2 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2)

        ps2 = ps2[0]
        self.assertEqual(ps2.message, 'O programa Z foi agendado com sucesso!')
        self.assertEqual(ps2.url, '/tv/api/1')
        # dt = datetime(2014, 4, 9, 18,53,13,0,tz)
        self.assertEqual(ps2.schedule_date, 1388657410)

        """
        Valida Update no registro do SetTopBox 2
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        urlrelation = jsdata['objects'][0]['resource_uri']
        response = self.c2.patch(urlrelation, data=json.dumps({
            'message': 'O programa YY foi agendado com sucesso!'}),
            content_type='application/json')
        self.assertEqual(202, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        ps2 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2)
        ps2 = ps2[0]
        self.assertEqual(
            ps2.message, 'O programa YY foi agendado com sucesso!'
        )

        """
        Valida aquisição de um agendamento especifico
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        urlrelation = jsdata['objects'][0]['resource_uri']
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)
        self.assertEqual(
            jsdata['message'],
            'O programa YY foi agendado com sucesso!'
        )

        """
        Validar se SetTopBox 1 pode remover
        agendamento em SetTopBox 2
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)
        response = self.c1.delete(jsdata['objects'][0]['resource_uri'])
        self.assertEqual(401, response.status_code)

        ps2 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2)

        """
        Validar se SetTopBox 1 pode atualizar
        agendamento em SetTopBox 2
        """

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        urlrelation = jsdata['objects'][0]['resource_uri']
        response = self.c1.patch(urlrelation, data=json.dumps({
            'message': 'O programa ZZ foi agendado com sucesso!'}),
            content_type='application/json')
        self.assertEqual(401, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        ps2 = SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2)
        ps2 = ps2[0]
        self.assertEqual(
            ps2.message, 'O programa YY foi agendado com sucesso!'
        )


class RemoteControlTest(TestCase):

    def setUp(self):
        log.debug('RemoteControlTest::setUp')
        from django.contrib.auth.models import User
        SetTopBox = apps.get_model('client', 'SetTopBox')

        self.user = User.objects.create_user(
            'adm', 'adm@cianet.ind.br', '123'
        )
        self.c = client.Client()
        SetTopBox.objects.create(
            serial_number='lululu', mac='FF:A0:00:00:01:61'
        )
        SetTopBox.objects.create(
            serial_number='lalala', mac='FF:21:30:70:64:33'
        )
        SetTopBox.objects.create(
            serial_number='lelele', mac='00:1A:D0:1A:D3:CA'
        )

    def test_api_get_settopbox(self):
        url_get = reverse(
            'client_v1:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'}
        )
        self.c.login(username='adm', password='123')
        response = self.c.get(url_get)
        self.assertEqual(response.status_code, 200)
        jobj = json.loads(response.content)
        log.debug('Conteudo=%s', jobj)

    def test_call_channel(self):
        Server = apps.get_model('device', 'Server')
        # mac[]=FF:21:30:70:64:33&mac[]=FF:01:67:77:21:80&mac[]=FF:32:32:26:11:21
        # ['FF:21:30:70:64:33', 'FF:01:67:77:21:80', 'FF:32:32:26:11:21']
        server, created = Server.objects.get_or_create(
            host='127.0.0.1', offline_mode=True
        )
        server.name = 'local'
        server.ssh_port = 22
        server.username = 'nginx'
        server.rsakey = '~/.ssh/id_rsa'
        server.offline_mode = True
        server.status = False
        server.save()
        obj = resolve(
            '/tv/client/route/FF:21:30:70:64:33;FF:01:67:77:21:80;'
            'FF:32:32:26:11:21/key/tv/1'
        )
        log.debug('req=%s', obj)
        url = reverse('client_route', kwargs={'stbs': ';'.join(
            ['FF:21:30:70:64:33', 'FF:01:67:77:21:80', 'FF:32:32:26:11:21']
        ), 'key': 'key', 'cmd': 'tv/1'})
        log.debug('rev=%s', url)
        response = self.c.get(url)
        self.assertEqual('{"status": "OK"}', response.content)
        self.assertEqual(
            '/tv/client/route/FF%3A21%3A30%3A70%3A64%3A33%3BFF%3A01%3A67%3A77'
            '%3A21%3A80%3BFF%3A32%3A32%3A26%3A11%3A21/key/tv/1', url
        )

    def test_reload_channels(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.objects.create(
            serial_number='do_helber', mac='FF:00:00:00:01:61'
        )
        url = reverse('client_reload_channels', kwargs={'stbs': ';'.join([
            'FF:00:00:00:01:61',
            'FF:21:30:70:64:33',
            '00:1A:D0:1A:D3:CA',
            'FF:A0:00:00:01:61'
        ]), 'message': 'Mensagem de teste;;/dsa'})
        self.assertEqual(
            url, '/tv/client/commands/reload_channels/FF%3A00%3A00%3A00%3A01'
            '%3A61%3BFF%3A21%3A30%3A70%3A64%3A33%3B00%3A1A%3AD0%3A1A%3AD3%3'
            'ACA%3BFF%3AA0%3A00%3A00%3A01%3A61/Mensagem%20de%20teste%3B%3B/dsa'
        )


class ParentSetTopBoxTest(TestCase):
    def setUp(self):
        log.debug('ParentSetTopBoxTest::setUp')
        from django.contrib.auth.models import User
        SetTopBox = apps.get_model('client', 'SetTopBox')

        SetTopBox.objects.create(
            serial_number='lululu', mac='FF:A0:00:00:01:61'
        )
        SetTopBox.objects.create(
            serial_number='lalala', mac='FF:21:30:70:64:33'
        )
        SetTopBox.objects.create(
            serial_number='lelele', mac='00:1A:D0:1A:D3:CA'
        )

    def test_selected_principal(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        stb1 = SetTopBox.objects.get(serial_number='lalala')
        stb2 = SetTopBox.objects.get(serial_number='lelele')

        stb2.parent = stb1
        stb2.save()
        self.assertEqual(stb2.parent, stb1)

    def test_selected_principal_with_principal(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        stb1 = SetTopBox.objects.get(serial_number='lalala')
        stb2 = SetTopBox.objects.get(serial_number='lelele')
        stb3 = SetTopBox.objects.get(serial_number='lelele')

        stb2.parent = stb1
        stb2.save()
        stb3.parent = stb2
        stb3.save()

        self.assertEqual(stb3.parent, None)

    def test_selected_principal_to_principal(self):
        SetTopBox = apps.get_model('client', 'SetTopBox')

        stb1 = SetTopBox.objects.get(serial_number='lalala')
        stb2 = SetTopBox.objects.get(serial_number='lelele')
        stb3 = SetTopBox.objects.get(serial_number='lelele')

        stb2.parent = stb1
        stb2.save()
        stb1.parent = stb3
        stb1.save()

        self.assertEqual(stb3.parent, None)