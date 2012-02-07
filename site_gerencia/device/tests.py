"""

"""

from django.test import TestCase

class ConnectionTest(TestCase):
    def test_connection(self):
        from models import Server
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 22
        srv.username = 'nginx'
        #srv.password = 'iptv'
        srv.rsakey = '/home/helber/.ssh/id_rsa_test'
        srv.connect()
        ret = srv.execute('/bin/pwd')
        #print(ret)
        self.asserttEqual(ret, '/var/lib/nginx\n', 'O home deveria ser "/var/lib/nginx\n"')
    
    def test_register_server(self):
        from models import Server
        