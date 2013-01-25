# -*- encoding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
#from django.test import Client
import simplejson as json
from models import SetTopBox
from models import SetTopBoxChannel
from device import models as devicemodels
from tv import models as tvmodels

from django.test.client import Client, FakePayload, MULTIPART_CONTENT
from django.test import client
from urlparse import urlparse


def patch_request_factory():
    def _method(self, path, data='', content_type='application/octet-stream', follow=False, **extra):
        response = self.generic("PATCH", path, data, content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    if not hasattr(client, "_patched"):
        client._patched = True
        client.Client.patch = _method


class Client2(Client):
    """
    Construct a second test client which can do PATCH requests.
    http://digidayoff.com/2012/03/01/unit-testing-patch-requests-with-djangos-test-client/
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PATCH request."
        print(data)
        patch_data = self._encode_data(data, content_type)
        print(patch_data)
        parsed = urlparse(path)
        print(parsed)
        r = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(patch_data),
        }
        r.update(extra)
        print(r)
        return self.request(**r)


#curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"serial_number": "lala"}' http://127.0.0.1:8000/tv/api/client/v1/settopbox/
#HTTP/1.0 201 CREATED
#Date: Fri, 10 Aug 2012 21:23:43 GMT
#Server: WSGIServer/0.1 Python/2.7.3
#Content-Type: text/html; charset=utf-8
#Location: http://127.0.0.1:8000/tv/api/client/v1/settopbox/1/


#curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"objects": [{"serial_number": "abc"}, {"serial_number": "efg"}, {"serial_number": "hij"}, {"serial_number": "aeh"}]}' http://127.0.0.1:8000/tv/api/client/v1/settopbox/


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

    def test_SetTopBox(self):
        from django.contrib.auth.models import User, Permission
        patch_request_factory()
        c = Client2()
        # Buscando o schema
        urlschema = reverse('client:api_get_schema',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1'})
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
        user = User.objects.create_user('erp', 'erp@cianet.ind.br', '123')
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
        # Create multiples (4) stbs in one call
        objects = {'objects': [
                {'serial_number': 'abc'},
                {'serial_number': 'efg'},
                {'serial_number': 'hij'},
                {'serial_number': 'aeh'}
            ]}
        serialized = json.dumps(objects)
        response = c.patch(url, data=serialized,
            content_type='application/json')
        self.assertEqual(response.status_code, 202)
        stbs = SetTopBox.objects.all()
        self.assertEqual(5, stbs.count())
        # Try to add new stb with existing serial_number
        response = c.post(url, data=json.dumps({'serial_number': 'lalala'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Error message on duplicated serial_number
        self.assertContains(response,
            'Duplicate entry for settopbox.serial_number',
            status_code=400)
        # Delete one stb
        urldelete = reverse('client:api_dispatch_detail',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1', 'pk': 2},
            )
        response = c.delete(urldelete)
        # Deve retornar 401 UNAUTHORIZED
        self.assertEqual(response.status_code, 401)
        # Add authorization to DELETE
        perm_delete_stb = Permission.objects.get(codename='delete_settopbox')
        #print(perm_delete_stb)
        user.user_permissions.add(perm_delete_stb)
        user.save()
        response = c.delete(urldelete)
        self.assertEqual(204, response.status_code)
        stbs = SetTopBox.objects.all()
        self.assertEqual(4, len(stbs))
        # Try to edit one settop box


class SetTopBoxChannelTest(TestCase):

    def setUp(self):
        import getpass
        from django.contrib.auth.models import User, Permission
        super(SetTopBoxChannelTest, self).setUp()
        self.c = Client2()
        self.user = User.objects.create_user('erp', 'erp@cianet.ind.br', '123')
        urllogin = reverse('sys_login')
        response = self.c.post(urllogin,
            {'username': 'erp', 'password': '123'},
            follow=True)
        self.assertEqual(response.status_code, 200)
        perm_add_relation = Permission.objects.get(
            codename='add_settopboxchannel')
        self.user.user_permissions.add(perm_add_relation)
        server = devicemodels.Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
            offline_mode=True,
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
        SetTopBox.objects.create(serial_number=u'lalala')
        SetTopBox.objects.create(serial_number=u'lelele')
        SetTopBox.objects.create(serial_number=u'lilili')
        SetTopBox.objects.create(serial_number=u'lololo')
        SetTopBox.objects.create(serial_number=u'lululu')

    def test_channel_stb(self):
        self.assertEqual(tvmodels.Channel.objects.all().count(), 3)
        self.assertEqual(SetTopBox.objects.all().count(), 5)
        # Get channel list
        urlchannels = reverse('client:api_dispatch_list', kwargs={
            'resource_name': 'channel', 'api_name': 'v1'})
        response = self.c.get(urlchannels)
        self.assertEqual(200, response.status_code)
        jobj = json.loads(response.content)
        # Ensure there is 3 channels in list
        self.assertEqual(3, jobj['meta']['total_count'])
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
            'channel': '/tv/api/client/v1/channel/2/'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = self.c.post(urlrelation, data=json.dumps({
            'settopbox': '/tv/api/client/v1/settopbox/2/',
            'channel': '/tv/api/client/v1/channel/2/'}),
            content_type='application/json')
        # Retorna erro ao criar uma associação duplicada
        response = self.c.post(urlrelation, data=json.dumps({
            'settopbox': '/tv/api/client/v1/settopbox/1/',
            'channel': '/tv/api/client/v1/channel/2/'}),
            content_type='application/json')
        self.assertEqual(400, response.status_code)
        # Respond properly error message on duplicated
        self.assertContains(response, 'Duplicate entry', status_code=400)


#class APITestSlumber(TestCase):
