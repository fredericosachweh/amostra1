#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários
"""

from django.test import TestCase


class GenericSourceTest(TestCase):
    
    def test_vlc_source(self):
        from device.models import Vlc, UniqueIP, Server
        s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='root',
            rsakey='~/.ssh/id_rsa_test'
        )
        s.connect()
        s.save()
        vlc = Vlc(server=s,description='VLC - generico')
        vlc.sink = '/home/videos/ros.avi'
        vlc.save()
        ip = UniqueIP()
        ip.sink = vlc
        ip.ip = ip._gen_ip()
        ip.save()
        nip = UniqueIP.objects.get(content_type=ip.content_type.id,object_id=vlc.pk)
        nip.sink.start()
        

class UniqueIPTest(TestCase):
    
    def test_sequential(self):
        from device.models import UniqueIP
        for i in range(1024):
            ip1 = UniqueIP()
            ip1.save()
            #print(ip1._gen_ip())


class ConnectionTest(TestCase):
    """
    Executa os testes de conexão com servidor local e remoto
    """
    
    def test_connection(self):
        "Teste de conexão com o usuário nginx no servidor local"
        from models import Server
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 22
        srv.username = 'nginx'
        #srv.password = 'iptv'
        srv.rsakey = '~/.ssh/id_rsa_test'
        srv.connect()
        ret = srv.execute('/bin/pwd')
        self.assertEqual(
            ret[0],
            '/var/lib/nginx\n',
            'O home deveria ser "/var/lib/nginx\n"'
        )
    
    def test_connection_failure(self):
        from models import Server
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 2222
        srv.username = 'nginx'
        srv.rsakey = '~/.ssh/id_rsa_test'
        srv.connect()
        self.assertEqual(str(srv.msg),
            'Unable to connect to 127.0.0.1: [Errno 111] Connection refused',
            'Deveria dar erro de conexão')
        self.assertFalse(srv.status, 'O status da conexão deveria ser False')

    def test_low_respose_command(self):
        "Test de comando demorado para executar"
        from lib.ssh import Connection
        conn = Connection('127.0.0.1',username='nginx',password='iptv')
        t = conn.execute_with_timeout('/var/lib/nginx/test',timeout=2)
        self.assertEqual(
            'Inicio\nP1**********Fim',
            t,
            'Valor esperado diferente [%s]' % t
        )

    def test_scan_channel(self):
        from lib.ssh import Connection
        c = Connection('172.17.0.2',
            username='helber',
            private_key='~/.ssh/id_rsa_cianet')
        c.execute_with_timeout(
            '/usr/bin/dvblast -a 0 -f 3642000 -s 4370000',
            timeout=2)


class ServerTest(TestCase):
    
    def setUp(self):
        from models import Server
        self.s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa_test'
        )
    
    def test_list_dir(self):
        l = self.s.list_dir('/')
        self.assertGreater( l.count('boot') , 0 ,
            'Deveria existir o diretório boot')
        self.assertGreater( l.count('bin') , 0 ,
            'Deveria existir o diretório bin')
        self.assertGreater( l.count('usr') , 0 ,
            'Deveria existir o diretório usr')

class ProcessControlTest(TestCase):

    def setUp(self):
        from models import Server
        self.s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa_test'
        )

    def test_prepare_daemon(self):
        import os
        cmd = '/usr/bin/cvlc -I dummy -v -R \
/mnt/projetos/gerais/videos/NovosOriginais/red_ridding_hood_4M.ts \
--sout "#std{access=udp,mux=ts,dst=192.168.0.244:5000}"'
        parsed = os.path.basename(cmd.split()[0])
        self.assertEqual(parsed, 'cvlc', 'Deveria ser retornado o comando')
        #fullcmd = '/usr/sbin/daemonize -p ~/%s-%s.pid %s' %(parsed,uid,cmd)

    def test_list_process(self):
        self.s.connect()
        procs = self.s.list_process()
        self.assertEqual(procs[0]['pid'],
            1,
            'O primero processo deveria ter pid=1')

    def test_start_process(self):
        cmd = '/usr/bin/cvlc -I dummy -v -R \
/mnt/projetos/gerais/videos/NovosOriginais/red_ridding_hood_4M.ts \
--sout "#std{access=udp,mux=ts,dst=239.1.1.5:5000}"'
        pid = self.s.execute_daemon(cmd)
        self.assertGreater(pid, 0, 'O processo deveria ser maios que zero')
        self.s.kill_process(pid)
        self.assertFalse(self.s.process_alive(pid),
            'O processo pid=%d deveria ter morrido.' % pid )


class RouteDeviceTest(TestCase):

    def setUp(self):
        from models import Server
        self.s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='root',
            rsakey='~/.ssh/id_rsa_test'
        )

    def test_list_iface(self):
        self.s.connect()
        ifaces = self.s.list_interfaces()
    
    def test_local_dev(self):
        self.s.connect()
        iface = self.s.get_netdev('127.0.0.1')
        self.assertEqual(iface, 'lo', 'Deveria ser a interface de loopback')
    
    def test_create_route(self):
        self.s.connect()
        self.s.create_route('239.0.1.10', 'p7p1')
        self.s.delete_route('239.0.1.10', 'p7p1')
