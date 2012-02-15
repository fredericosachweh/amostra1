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
        self.assertEqual(ret[0], '/var/lib/nginx\n', 'O home deveria ser "/var/lib/nginx\n"')
    
    #def test_register_server(self):
    #    from lib.ssh import Connection
    #    c = Connection('127.0.0.1',username='nginx',password='iptv')
    #    k = c.genKey()
    #    #print(k)
    
    def test_low_respose_command(self):
        from lib.ssh import Connection
        c = Connection('127.0.0.1',username='nginx',password='iptv')
        #stdin, stdout, stderr = c.new_execute('/var/lib/nginx/test')
        t = c.new_execute('/var/lib/nginx/test')
        #print(t)
    
    def test_scan_channel(self):
        from lib.ssh import Connection
        c = Connection('172.17.0.2',username='helber',private_key='~/.ssh/id_rsa_cianet')
        #r = c.new_execute('/usr/bin/dvblast -a 1 -c /etc/dvblast/channels.d/2.conf -f 3390000 -s 7400000 -m psk_8 -U -u -d 239.0.1.1:10000')
        r = c.new_execute('/usr/bin/dvblast -a 0 -f 3090000 -s 2220000')
        #print(r)
    
    def test_control_dvb(self):
        self.assertFalse(False, 'Criar o controle de processos do dvb')
    
    def test_control_multicat(self):
        self.assertFalse(False, 'Criar o controle de processos do multicat')
    
    def test_remote_process(self):
        pass


