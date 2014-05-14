# -*- encoding:utf-8 -*-

import simplejson as json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings
from django.test.client import Client, FakePayload, MULTIPART_CONTENT
from django.test import client
from django.utils import timezone
from urlparse import urlparse
from models import SetTopBox
from device import models as devicemodels
from tv import models as tvmodels

import models
import logging
import simplejson
from datetime import tzinfo, timedelta

log = logging.getLogger('unittest')

def patch_request_factory():
    def _method(self, path, data='', content_type='application/octet-stream',
            follow=False, **extra):
        response = self.generic("PATCH", path, data, content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    if not hasattr(client, "_patched"):
        client._patched = True
        client.Client.patch = _method


class Client2(Client):
    u"""
    Construct a second test client which can do PATCH requests.
    http://digidayoff.com/2012/03/01/unit-testing-patch-requests-with-djangos-\
test-client/
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PATCH request."
        patch_data = self._encode_data(data, content_type)
        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': self._get_path(parsed),
            'QUERY_STRING': parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input': FakePayload(patch_data),
        }
        r.update(extra)
        return self.request(**r)


#curl --dump-header - -H "Content-Type: application/json" -X POST --data \
#'{"serial_number": "lala"}' http://127.0.0.1:8000/tv/api/client/v1/settopbox/
#HTTP/1.0 201 CREATED
#Date: Fri, 10 Aug 2012 21:23:43 GMT
#Server: WSGIServer/0.1 Python/2.7.3
#Content-Type: text/html; charset=utf-8
#Location: http://127.0.0.1:8000/tv/api/client/v1/settopbox/1/


#curl --dump-header - -H "Content-Type: application/json" -X POST --data \
#'{"objects": [{"serial_number": "abc"}, {"serial_number": "efg"}, \
#{"serial_number": "hij"}, {"serial_number": "aeh"}]}' \
#http://127.0.0.1:8000/tv/api/client/v1/settopbox/


class APITest(TestCase):
    u'''
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
        self.user = User.objects.create_user('erp', 'erp@cianet.ind.br',
            '123')

    def test_SetTopBox(self):
        from django.contrib.auth.models import Permission
        SetTopBox.options.auto_create = False
        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True
        patch_request_factory()
        #c = Client2(enforce_csrf_checks=False)
        c = Client()
        # Buscando o schema
        urlschema = reverse('client:api_get_schema',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'})
        #self.encoded_creds = "Basic " + "demo:demo".encode("base64")
        c.login(username='erp', password='123')
        response = c.get(urlschema)
        jschema = json.loads(response.content)
        self.assertEqual('string', jschema['fields']['serial_number']['type'])
        # Buscando lista
        url = reverse('client:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'},
            )
        response = c.get(url)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        # Try to create new settopbox using post on api, but need to logged in
        response = c.post(url, data=json.dumps({'serial_number': 'lalala'}),
            content_type='application/json')
        self.assertEqual(401, response.status_code)
        # Create new user and do login to into middlewer
        #user = User.objects.create_user('erp', 'erp@cianet.ind.br', '123')
        user = self.user
        urllogin = reverse('sys_login')
        response = c.post(urllogin, {'username': 'erp', 'password': '123'},
            follow=True)
        self.assertEqual(response.status_code, 200)
        # Try again and responds with no permission
        response = c.post(url, data=json.dumps({'serial_number': 'lalala'}),
            content_type='application/json')
        self.assertEqual(401, response.status_code)
        # Create permission to create stb
        perm_add_stb = Permission.objects.get(codename='add_settopbox')
        user.user_permissions.add(perm_add_stb)
        user.save()
        # Create new settopbox using post
        response = c.post(url, data=json.dumps({'serial_number': 'lalala'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)
        stbs = SetTopBox.objects.all()
        self.assertEqual(1, stbs.count())
        self.assertEqual('lalala', stbs[0].serial_number)
        # Try to add new stb with existing serial_number
        response = c.post(url, data=json.dumps({'serial_number': 'lalala'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Error message on duplicated serial_number
        self.assertContains(response,
            'serial_number',
            status_code=400)
        # Delete one stb
        urldelete = reverse('client:api_dispatch_detail',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1', 'pk': 1},
            )
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
        c = Client()
        c.login(username='erp', password='123')
        #urllogin = reverse('sys_login')
        #response = c.post(urllogin, {'username': 'erp', 'password': '123'},
        #    follow=True)
        #self.assertEqual(response.status_code, 200)
        # Buscando lista
        url = reverse('client:api_dispatch_list',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'},
            )
        # Create multiples (4) stbs in one call
        objects = {'objects': [
                {'serial_number': 'abc', 'mac': 'abc'},
                {'serial_number': 'efg', 'mac': 'efg'},
                {'serial_number': 'hij', 'mac': 'hij'},
                {'serial_number': 'aeh', 'mac': 'aeh'}
            ]}
        serialized = json.dumps(objects)
        p = self.user.user_permissions
        p.add(Permission.objects.get(codename='add_settopbox'))
        p.add(Permission.objects.get(codename='change_settopbox'))
        p.add(Permission.objects.get(codename='delete_settopbox'))
        #self.user.save()
        response = c.patch(url, data=serialized,
            content_type='application/json')
        self.assertEqual(response.status_code, 202)
        stbs = SetTopBox.objects.all()
        self.assertEqual(4, stbs.count())


@override_settings(DVBLAST_COMMAND=settings.DVBLAST_DUMMY)
@override_settings(DVBLASTCTL_COMMAND=settings.DVBLASTCTL_DUMMY)
@override_settings(MULTICAT_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(MULTICATCTL_COMMAND=settings.MULTICATCTL_DUMMY)
@override_settings(VLC_COMMAND=settings.VLC_DUMMY)
class SetTopBoxChannelTest(TestCase):

    def setUp(self):
        #import getpass
        from django.contrib.auth.models import User, Permission
        super(SetTopBoxChannelTest, self).setUp()
        self.c = Client()
        self.user = User.objects.create_user('erp', 'erp@cianet.ind.br', '123')
        self.user.is_staff = True
        self.user.save()
        urllogin = reverse('sys_login')
        response = self.c.post(urllogin,
            {'username': 'erp', 'password': '123'},
            follow=True)
        self.assertEqual(response.status_code, 200)
        perm_add_relation = Permission.objects.get(
            codename='add_settopboxchannel')
        self.user.user_permissions.add(perm_add_relation)
        perm_delete_relation = Permission.objects.get(
            codename='delete_settopboxchannel')
        self.user.user_permissions.add(perm_delete_relation)
        server = devicemodels.Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',  # getpass.getuser(),
            rsakey='~/.ssh/id_rsa'
        )
        nic = devicemodels.NIC.objects.create(server=server, ipv4='127.0.0.1')
        unicastin = devicemodels.UnicastInput.objects.create(
            server=server,
            interface=nic,
            port=30000,
            protocol='udp',
        )
        service = devicemodels.DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )
        internal = devicemodels.UniqueIP.create(sink=service)
        ipout1 = devicemodels.MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.2',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        ipout2 = devicemodels.MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        ipout3 = devicemodels.MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.4',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        self.ipout4 = devicemodels.MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.5',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        self.channel1 = tvmodels.Channel.objects.create(
            number=51,
            name='Discovery Channel',
            description='Cool tv channel',
            channelid='DIS',
            image='',
            enabled=True,
            source=ipout1,
        )
        self.channel2 = tvmodels.Channel.objects.create(
            number=13,
            name='Globo',
            description=u'Rede globo de televisão',
            channelid='GLB',
            image='',
            enabled=True,
            source=ipout2,
            )
        self.channel3 = tvmodels.Channel.objects.create(
            number=14,
            name='Test 3',
            description=u'Rede Test 3',
            channelid='RIC',
            image='',
            enabled=True,
            source=ipout3,
            )
        storage = devicemodels.Storage.objects.create(
            folder='/tmp/test_record',
            server=server
            )
        self.rec1 = devicemodels.StreamRecorder.objects.create(
            channel=self.channel1,
            rotate=5,
            storage=storage,
            keep_time=10,
            nic_sink=nic,
            server=server
            )
        self.rec2 = devicemodels.StreamRecorder.objects.create(
            channel=self.channel2,
            rotate=5,
            storage=storage,
            keep_time=20,
            nic_sink=nic,
            server=server
            )
        self.rec3 = devicemodels.StreamRecorder.objects.create(
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
        self.assertEqual(tvmodels.Channel.objects.all().count(), 3)
        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = True
        self.assertEqual(SetTopBox.options.auto_add_channel, False)
        SetTopBox.objects.create(serial_number=u'lalala', mac=u'lalala')
        SetTopBox.objects.create(serial_number=u'lelele', mac=u'lelele')
        SetTopBox.objects.create(serial_number=u'lilili', mac=u'lilili')
        SetTopBox.objects.create(serial_number=u'lololo', mac=u'lololo')
        SetTopBox.objects.create(serial_number=u'lululu', mac=u'lululu')
        self.assertEqual(SetTopBox.objects.all().count(), 5)
        # Get channel list
        urlchannels = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        response = self.c.get(urlchannels)
        self.assertEqual(200, response.status_code)
        jobj = json.loads(response.content)
        # Ensure there is 3 channels in list
        self.assertEqual(3, jobj['meta']['total_count'])

        urllogin = reverse('sys_login')
        response = self.c.post(urllogin,
            {'username': 'erp', 'password': '123'},
            follow=True)
        self.assertEqual(response.status_code, 200)

        # Get stb list
        urlstb = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopbox', 'api_name': 'v1'})
        response = self.c.get(urlstb)
        jobj = json.loads(response.content)
        # Ensure there is 5 settopbox in list
        self.assertEqual(5, jobj['meta']['total_count'])
        # Add relation bethen stb and 2 channels
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxchannel', 'api_name': 'v1'})
        response = self.c.post(urlrelation, data=json.dumps({
            'settopbox': '/tv/api/client/v1/settopbox/1/',
            'channel': '/tv/api/tv/v1/channel/2/',
            'recorder': True}),
            content_type='application/json')
        self.assertEqual(response.status_code, 201,
            'Content:%s' % response.content)
        response = self.c.post(urlrelation, data=json.dumps({
            'settopbox': '/tv/api/client/v1/settopbox/2/',
            'channel': '/tv/api/tv/v1/channel/2/',
            'recorder': True}),
            content_type='application/json')
        # Retorna erro ao criar uma associação duplicada
        response = self.c.post(urlrelation, data=json.dumps({
            'settopbox': '/tv/api/client/v1/settopbox/1/',
            'channel': '/tv/api/tv/v1/channel/2/',
            'recorder': True}),
            content_type='application/json')
        self.assertEqual(400, response.status_code)
        # Respond properly error message on duplicated
        self.assertContains(response,
            'not unique',
            status_code=400)

    def test_settopbox_options(self):
        SetTopBox.options.auto_add_channel = False
        SetTopBox.options.use_mac_as_serial = True
        self.assertEqual(SetTopBox.options.auto_add_channel, False,
            'Default value not working')
        self.assertEqual(SetTopBox.options.use_mac_as_serial, True,
            'Default value not working')

    def test_auth_get(self):
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(response.status_code, 200)
        response = self.c.get(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(401, response.status_code)

    def test_settopbox_autologin(self):
        from django.contrib.auth.models import User
        ## Define auto_create and execute again
        models.SetTopBox.options.auto_create = False
        models.SetTopBox.options.auto_add_channel = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(403, response.status_code)
        ## Define auto_create and execute again
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        ## Busca o ususário criado para o stb
        user = User.objects.get(username=settings.STB_USER_PREFIX + \
            '01:02:03:04:05:06')
        ## Verifica se existe a relação criado nos 3 canais
        # Busca o stb
        stb = models.SetTopBox.objects.get(serial_number=u'01:02:03:04:05:06')
        self.assertEqual(user, stb.get_user())
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        # Número de stb-channel
        self.assertEqual(3, stb_ch.count())
        ## Remove o canal Globo
        self.channel2.delete()
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        self.assertEqual(2, stb_ch.count())
        ## Create new channel
        ch = tvmodels.Channel.objects.create(
            number=18,
            name='Globo 2',
            description=u'Rede globo 2 de televisão',
            channelid='GLB',
            image='',
            enabled=True,
            source=self.ipout4
            )
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb,
            channel=ch)
        self.assertEqual(1, stb_ch.count())
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:00',
            'sn': 123456})
        self.assertEqual(200, response.status_code)
        stb = models.SetTopBox.objects.get(serial_number=123456)
        ## Busca o ususário criado para o stb
        user = User.objects.get(username=settings.STB_USER_PREFIX + \
            '123456')
        self.assertEqual(user, stb.get_user())

    def test_case_insensitive_mac_sn(self):
        ## Define auto_create and execute again
        models.SetTopBox.options.auto_create = False
        models.SetTopBox.options.auto_add_channel = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        ## Define auto_create and execute again
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        ## Now disable auto_create
        models.SetTopBox.options.auto_create = False
        models.SetTopBox.options.auto_add_channel = False
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:00'})
        self.assertEqual(403, response.status_code)
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'mac': '01:02:03:04:05:06',
            'sn': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06',
            'SN': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)

    def test_get_channels_from_stb(self):
        ## Define auto_create and execute again
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        stb = models.SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        tvchannels = tvmodels.Channel.objects.all()
        try:
            channels = stb.get_channels()
        except Exception as e:
            self.assertFalse(True,
                'O metodo SetTopBox.get_channels() deveria existir:%s' % e)
        self.assertItemsEqual(channels, tvchannels)
        ## Remove uma relação
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
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
        ## Define auto_create and execute again
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        stb = models.SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        self.assertEqual(stb.serial_number, u'01:02:03:04:05:06')
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        self.assertEqual(3, stb_ch.count())
        url_channel = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        ## Get list of channels
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])
        ## Remove one relation
        stb_ch[2].delete()
        ## Check removed element
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        self.assertEqual(2, stb_ch.count())
        ## Get list of channels again
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        ## Ensure has 2 channels on response
        self.assertEqual(2, jobj['meta']['total_count'])
        ## Test Anonimous
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.get(url_channel)
        self.assertEqual(401, response.status_code)

    def test_list_records(self):
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        models.SetTopBox.options.auto_enable_recorder_access = False
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        ## Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        ## Call tvod_list
        url_tvod = reverse('device.views.tvod_list')
        self.assertEqual(url_tvod, '/tv/device/tvod_list/')
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        ## Do login
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        ## Get list of records
        recs = devicemodels.StreamRecorder.objects.all()
        self.assertEqual(3, recs.count())
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(0, jobj['meta']['total_count'])
        ## Get STB
        stb = models.SetTopBox.objects.get(serial_number='01:02:03:04:05:06')
        ## Get STB-ch relation
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        ## Enable record access to 1 channel
        rec = stb_ch[1]
        rec.recorder = True
        rec.save()
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        ## Call tvod_list
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(1, jobj['meta']['total_count'])
        ## Enable record access to second channel
        stb_ch = models.SetTopBoxChannel.objects.filter(settopbox=stb)
        stb_ch.update(recorder=True)
        ## Call tvod_list
        response = self.c.get(url_tvod)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])

    def test_play_record(self):
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        models.SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        ## Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        ## Try play recorder ch=13, 14, 51
        ## channel_number=None, command=None, seek=0
        url_play = reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'play',
            'seek': 20})
        self.assertEqual('/tv/device/tvod/13/play/20', url_play)
        response = self.c.get(url_play)
        self.assertEqual(401, response.status_code)
        ## Do login
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        ## No channel
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 15,
            'command': 'play',
            'seek': 20}))
        self.assertEqual(404, response.status_code)
        ## No seek avaliable
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'play',
            'seek': 200000}))
        self.assertEqual(404, response.status_code)
        ## All OK
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'play',
            'seek': 200}))
        self.assertEqual(200, response.status_code)
        response = self.c.get(reverse('device.views.tvod', kwargs={
            'channel_number': 13,
            'command': 'stop',
            'seek': 20}))
        self.assertEqual(200, response.status_code)

    def test_list_disable_channel(self):
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        models.SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        ## Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        url_channel = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        ## Get list of channels
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])
        self.channel2.enabled = False
        self.channel2.save()
        response = self.c.get(url_channel)
        jobj = json.loads(response.content)
        self.assertEqual(2, jobj['meta']['total_count'])

    def test_api_key_channel(self):
        from tastypie.models import ApiKey
        from django.contrib.auth.models import User
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        models.SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        ## Do logoff
        response = self.c.get(auth_logoff)
        self.assertEqual(200, response.status_code)
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)
        user = User.objects.get(username=settings.STB_USER_PREFIX + \
            '01:02:03:04:05:06')
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
        url_channel = reverse('tv_v1:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual('/tv/api/tv/v1/channel/', url_channel)
        ## Get empty list (Anonymous)
        response = self.c.get(url_channel)
        self.assertEqual(401, response.status_code)
        ## Get list of channels
        response = self.c.get(url_channel + '?api_key=%s' % api_key)
        jobj = json.loads(response.content)
        self.assertEqual(3, jobj['meta']['total_count'])


class TestRequests(TestCase):

    def setUp(self):
        self.c = Client()

    def test_call_login(self):
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        models.SetTopBox.options.auto_enable_recorder_access = True
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertContains(response, 'api_key')
        key = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key)
        ## Create new STBconfig
        url_config = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxconfig', 'api_name': 'v1'})
        self.assertEqual('/tv/api/client/v1/settopboxconfig/', url_config)
        ## Create a config
        data = simplejson.dumps({"key": "VOLUME_LEVEL", "value": "0.5",
            "value_type": "Number"})
        response = self.c.post(url_config, data=data,
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.has_header('location'))
        ## load stb config
        response = self.c.get(url_config)
        self.assertEqual(response.status_code, 200)
        jobj = simplejson.loads(response.content)
        self.assertEqual(jobj['meta']['total_count'], 3)
        ## login on new STB
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:07'})
        self.assertContains(response, 'api_key')
        key1 = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key1)
        data = simplejson.dumps({"key": "VOLUME_LEVEL", "value": "0.3",
            "value_type": "Number"})
        response = self.c.post(url_config, data=data,
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.has_header('location'))
        response = self.c.get(url_config)
        self.assertEqual(response.status_code, 200)
        jobj = simplejson.loads(response.content)
        self.assertEqual(jobj['meta']['total_count'], 3)
        ## Change volume value
        url_vol = reverse('client:api_dispatch_detail', kwargs={
            'resource_name': 'settopboxconfig', 'api_name': 'v1', 'pk': 5})
        self.assertEqual('/tv/api/client/v1/settopboxconfig/5/', url_vol)
        response = self.c.get('/tv/api/client/v1/settopboxconfig/')
        self.assertEqual(response.status_code, 200)
        data = simplejson.dumps({"value": "0.2"})
        response = self.c.put(url_vol, data=data,
            content_type='application/json')
        self.assertEqual(response.status_code, 204)
        conf = models.SetTopBoxConfig.objects.get(id=5)
        self.assertEqual(u'0.2', conf.value)
        response = self.c.get(auth_logoff)
        self.assertEqual(response.status_code, 200)
        response = self.c.get(url_vol + '?api_key=%s' % key)
        #log.debug('status_code=%s, content=%s', response.status_code,
        #    response.content)
        self.assertEqual(response.status_code, 400)


class TestDefaultConfig(TestCase):

    def setUp(self):
        self.c = Client()

    def test_call_login(self):
        models.SetTopBox.options.auto_create = True
        models.SetTopBox.options.auto_add_channel = True
        models.SetTopBox.options.use_mac_as_serial = True
        models.SetTopBox.options.auto_enable_recorder_access = True
        models.SetTopBox.default.password = '1234'
        models.SetTopBox.default.recorder = True
        models.SetTopBox.default.parental = '18'
        auth_login = reverse('client_auth')
        auth_logoff = reverse('client_logoff')
        response = self.c.post(auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertContains(response, 'api_key')
        key = json.loads(response.content).get('api_key', None)
        self.assertIsNotNone(key)
        ## Create new STBconfig
        url_config = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxconfig', 'api_name': 'v1'})
        self.assertEqual('/tv/api/client/v1/settopboxconfig/', url_config)
        response = self.c.get(url_config)
        self.assertContains(response, 'global.PASSWORD')
        self.assertContains(response, '1234')
        self.assertContains(response, 'app/tv.PARENTAL_CONTROL')
        self.assertContains(response, '"value": "18"')
        self.assertContains(response, '"value": "enable"')
        models.SetTopBox.default.password = '2222'
        models.SetTopBox.default.recorder = False
        models.SetTopBox.default.parental = '-1'
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

class SetTopBoxProgramScheduleTest(TestCase):

    def setUp(self):
        self.c1 = Client()
        self.c2 = Client()
        self.c3 = Client()
        self.auth_login = reverse('client_auth')
        self.auth_logoff = reverse('client_logoff')

        SetTopBox.options.auto_create = True
        SetTopBox.options.auto_add_channel = True
        SetTopBox.options.use_mac_as_serial = True
        SetTopBox.options.auto_enable_recorder_access = True

        server = devicemodels.Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',  # getpass.getuser(),
            rsakey='~/.ssh/id_rsa'
        )

        nic = devicemodels.NIC.objects.create(server=server, ipv4='127.0.0.1')

        unicastin = devicemodels.UnicastInput.objects.create(
            server=server,
            interface=nic,
            port=30000,
            protocol='udp',
        )

        service = devicemodels.DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )

        internal = devicemodels.UniqueIP.create(sink=service)

        ipout1 = devicemodels.MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.2',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )

        ipout2 = devicemodels.MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )

        channel1 = tvmodels.Channel.objects.create(
            number=51,
            name='Discovery Channel',
            description='Cool tv channel',
            channelid='DIS',
            image='',
            enabled=True,
            source=ipout1,
        )

        self.channel2 = tvmodels.Channel.objects.create(
            number=13,
            name='Globo',
            description=u'Rede globo de televisão',
            channelid='GLB',
            image='',
            enabled=True,
            source=ipout2,
            )

    def test_program_schedule(self):
        """
        Realiza login com settopbox 1 e settopbox 2
        """
        response = self.c1.post(self.auth_login, data={'MAC': '01:02:03:04:05:06'})
        self.assertEqual(200, response.status_code)

        response = self.c2.post(self.auth_login, data={'MAC': '01:02:03:04:05:07'})
        self.assertEqual(200, response.status_code)

        stb1 = models.SetTopBox.objects.get(serial_number=u'01:02:03:04:05:06')
        stb2 = models.SetTopBox.objects.get(serial_number=u'01:02:03:04:05:07')

        ch1 = tvmodels.Channel.objects.get(name='Discovery Channel')
        ch2 = tvmodels.Channel.objects.get(name='Globo')

        #tz = timezone.utc
        #post_date = datetime(2014, 4, 9, 18,53,13,0,tz)

        """
        Realiza um agendamento no settopbox 1 e dois agendamentos no settopbox 2
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c1.post(urlrelation, data=json.dumps({
            'settopbox': '1',
            'channel': '51',
            'url': u'/tv/api/1',
            'message': u'O programa Y foi agendado com sucesso!',
            'schedule_date':'1388657410'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.post(urlrelation, data=json.dumps({
            'settopbox': '1',
            'channel': '13',
            'url': u'/tv/api/1',
            'message': u'O programa X foi agendado com sucesso!',
            'schedule_date':'1388657410'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.post(urlrelation, data=json.dumps({
            'settopbox': '1',
            'channel': '13',
            'url': u'/tv/api/1',
            'message': u'O programa Z foi agendado com sucesso!',
            'schedule_date':'1388657410'}),
            content_type='application/json')
        self.assertEqual(201, response.status_code)

        """
        Valida dados de agendamento no settopbox 1 e settopbox 2
        """
        ps1 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb1)[0]
        ps2 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)[0]

        self.assertEqual(ps1.message, u'O programa Y foi agendado com sucesso!')
        self.assertEqual(ps1.url, u'/tv/api/1')
        #dt = datetime(2014, 4, 9, 18,53,13,0,tz)
        self.assertEqual(ps1.schedule_date, 1388657410)

        self.assertEqual(ps2.message, u'O programa X foi agendado com sucesso!')
        self.assertEqual(ps2.url, u'/tv/api/1')
        #dt = datetime(2014, 4, 9, 18,53,13,0,tz)
        self.assertEqual(ps2.schedule_date, 1388657410)

        ps1 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb1)
        self.assertEqual(ps1.count(), 1);

        """
        Remove agendamento no settopbox 1
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c1.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        response = self.c1.delete(jsdata['objects'][0]['resource_uri'])
        self.assertEqual(204, response.status_code)

        """
        Valida remoção do agendamento no settopbox 1
        """
        ps1 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb1)
        self.assertEqual(ps1.count(), 0);

        """
        Realiza login com settopbox 3
        """
        response = self.c3.post(self.auth_login, data={'MAC': '01:02:03:04:05:08'})
        self.assertEqual(200, response.status_code)

        stb3 = models.SetTopBox.objects.get(serial_number=u'01:02:03:04:05:08')

        """
        Valida se o settopbox 3 não possui agendamentos
        """
        ps3 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb3)
        self.assertEqual(ps3.count(), 0)

        """
        Valida se a remoção do agendamento no settopbox 1 não influenciou no agendamento do settopbox 2
        """
        stb2 = models.SetTopBox.objects.get(serial_number=u'01:02:03:04:05:07')

        ps2 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2);

        ps2 = ps2[0]
        self.assertEqual(ps2.message, u'O programa X foi agendado com sucesso!')
        self.assertEqual(ps2.url, u'/tv/api/1')
        #dt = datetime(2014, 4, 9, 18,53,13,0,tz)
        self.assertEqual(ps2.schedule_date, 1388657410)

        """
        Valida Update no registro do settopbox 2
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        urlrelation = jsdata['objects'][0]['resource_uri']
        response = self.c2.patch(urlrelation, data=json.dumps({
            'message': u'O programa YY foi agendado com sucesso!'}),
            content_type='application/json')
        self.assertEqual(202, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        ps2 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2);
        ps2 = ps2[0]
        self.assertEqual(ps2.message, u'O programa YY foi agendado com sucesso!')

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
        self.assertEqual(jsdata['message'], u'O programa YY foi agendado com sucesso!')

        """
        Validar se settopbox 1 pode remover agendamento em settopbox 2
        """
        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)
        response = self.c1.delete(jsdata['objects'][0]['resource_uri'])
        self.assertEqual(401, response.status_code)

        ps2 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2);

        """
        Validar se settopbox 1 pode atualizar agendamento em settopbox 2
        """

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        jsdata = json.loads(response.content)

        urlrelation = jsdata['objects'][0]['resource_uri']
        response = self.c1.patch(urlrelation, data=json.dumps({
            'message': u'O programa ZZ foi agendado com sucesso!'}),
            content_type='application/json')
        self.assertEqual(401, response.status_code)

        urlrelation = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'settopboxprogramschedule', 'api_name': 'v1'})
        response = self.c2.get(urlrelation)
        self.assertEqual(200, response.status_code)

        ps2 = models.SetTopBoxProgramSchedule.objects.filter(settopbox=stb2)
        self.assertEqual(ps2.count(), 2);
        ps2 = ps2[0]
        self.assertEqual(ps2.message, u'O programa YY foi agendado com sucesso!')
