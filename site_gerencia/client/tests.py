# -*- encoding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
#from django.test import Client
import simplejson as json
from models import SetTopBox

from django.test.client import Client, FakePayload, MULTIPART_CONTENT
from urlparse import urlparse


class Client2(Client):
    """
    Construct a second test client which can do PATCH requests.
    http://digidayoff.com/2012/03/01/unit-testing-patch-requests-with-djangos-test-client/
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PATCH request."
        patch_data = self._encode_data(data, content_type)
        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(patch_data),
        }
        r.update(extra)
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
        print(stbs)
        self.assertEqual(5, stbs.count())
        # Try to add new stb with existing serial_number
        response = c.post(url, data=json.dumps({'serial_number': 'lalala'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 500)
        # TODO: Return correct message
        #self.assertContains(response, 'duplicated value serial_number',
        #    status_code=500)
        # Delete one stb
        urldelete = reverse('client:api_dispatch_detail',
            kwargs={'resource_name': 'settopbox', 'api_name': 'v1', 'pk': 2},
            )
        response = c.get('/tv/api/client/v1/settopbox/2/')
        print(response.status_code)
        print(response.content)
        print(urldelete)
        response = c.delete('/tv/api/client/v1/settopbox/2/')
        print(response.content)
        self.assertEqual(response.status_code, 204)
        stbs = SetTopBox.objects.all()
        print(stbs)
        # Try to edit one settop box
