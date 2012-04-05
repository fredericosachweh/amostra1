#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários
"""

from django.test import TestCase

class CommandsGenerationTest(TestCase):
    def setUp(self):
        from device.models import Server, Antenna, DvbTuner, IsdbTuner, \
            DemuxedService, UniqueIP, MulticastOutput, NIC, StreamRecorder
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='iptv',
            password='iptv',
        )
        nic = NIC.objects.create(
            server=server,
            name='eth0',
            ipv4='192.168.0.10',
        )
        antenna = Antenna.objects.create(
            satellite='StarOne C2',
            lnb_type='multiponto_c',
        )
        dvbtuner = DvbTuner.objects.create(
            server=server,
            antenna=antenna,
            frequency=3990,
            symbol_rate=7400,
            modulation='8PSK',
            polarization='H',
            fec='34',
            adapter='00:00:00:00:00:00',
        )
        isdbtuner = IsdbTuner.objects.create(
            server=server,
            frequency=587143,
            bandwidth=6,
            modulation='qam',
        )
        service_a = DemuxedService.objects.create(
            sid=1,
            sink=dvbtuner,
        )
        service_b = DemuxedService.objects.create(
            sid=2,
            sink=dvbtuner,
        )
        service_c = DemuxedService.objects.create(
            sid=3,
            sink=dvbtuner,
        )
        service_d = DemuxedService.objects.create(
            sid=1,
            sink=isdbtuner,
        )
        internal_a = UniqueIP.objects.create(
            port=20000,
            sink=service_a,
            nic=NIC.objects.filter(server=server)[0],
        )
        internal_b = UniqueIP.objects.create(
            port=20000,
            sink=service_b,
            nic=NIC.objects.filter(server=server)[0],
        )
        internal_c = UniqueIP.objects.create(
            port=20000,
            sink=service_d,
            nic=NIC.objects.filter(server=server)[0],
        )
        ipout_a = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.3',
            port=10000,
            protocol='udp',
            interface='127.0.0.1',
            sink=internal_a,
        )
        recorder = StreamRecorder.objects.create(
            server=server,
            rotate=60,
            folder='/tmp/recording',
            sink=internal_a,
        )
        ipout_b = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.4',
            port=10000,
            protocol='udp',
            interface='127.0.0.1',
            sink=internal_c,
        )
    
    def test_dvbtuner(self):
        from models import DvbTuner
        tuner = DvbTuner.objects.get(pk=1)
        expected_cmd = (
            "/usr/bin/dvblast "
            "-f 3390000 "
            "-m psk_8 "
            "-s 7400000 "
            "-F 34 "
            "-a 0 "
            "-c /etc/dvblast/channels.d/1.conf "
            "-r /var/run/dvblast/sockets/1.sock "
            "&> /var/log/dvblast/1.log"
        )
        self.assertEqual(expected_cmd, tuner._get_cmd(adapter_num=0))
        
        expected_conf = u'239.1.0.2:20000/udp 1 1\n239.1.0.3:20000/udp 1 2\n'
        self.assertEqual(expected_conf, tuner._get_config())
    
    def test_isdbtuner(self):
        from models import IsdbTuner
        tuner = IsdbTuner.objects.get(pk=2)
        expected_cmd = (
            "/usr/bin/dvblast "
            "-f 587143000 "
            "-m qam_auto "
            "-b 6 "
            "-a 1 "
            "-c /etc/dvblast/channels.d/2.conf "
            "-r /var/run/dvblast/sockets/2.sock "
            "&> /var/log/dvblast/2.log"
        )
        self.assertEqual(expected_cmd, tuner._get_cmd(adapter_num=1))
    
    def test_multicastoutput(self):
        from models import MulticastOutput
        ipout = MulticastOutput.objects.get(pk=3)
        expected_cmd = (
            "/usr/bin/multicat "
            "-c /var/run/multicat/sockets/3.sock "
            "-u @239.1.0.2:20000 "
            "-U 239.0.1.3:10000 "
            "&> /var/log/multicat/3.log"
        )
        self.assertEqual(expected_cmd, ipout._get_cmd())
    
    def test_streamrecorder(self):
        from models import StreamRecorder
        recorder = StreamRecorder.objects.get(pk=4)
        expected_cmd = (
            "/usr/bin/multicat "
            "-c /var/run/multicat/sockets/4.sock "
            "-u @239.1.0.2:20000 "
            "/var/lib/multicat/recordings/4 "
            "&> /var/log/multicat/4.log"
        )
        self.assertEqual(expected_cmd, recorder._get_cmd())

class GenericSourceTest(TestCase):
    
    def test_vlc_source(self):
        from device.models import Vlc, UniqueIP, Server, NIC
        s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='root',
            rsakey='~/.ssh/id_rsa_test'
        )
        s.connect()
        s.save()
        s.auto_create_nic()
        nics = NIC.objects.filter(server=s)
        vlc = Vlc(server=s,description='VLC - generico')
        vlc.sink = '/home/videos/ros.avi'
        vlc.save()
        ip = UniqueIP()
        ip.sink = vlc
        ip.nic = nics[1]
        ip.ip = ip._gen_ip()
        ip.save()
        nip = UniqueIP.objects.get(content_type=ip.content_type.id,object_id=vlc.pk)
        nip.sink.start()

class UniqueIPTest(TestCase):
    
    def test_sequential(self):
        from device.models import UniqueIP
        for i in range(1024):
            ip1 = UniqueIP()
            #ip1.save()
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
        self.assertGreater(pid, 0, 'O processo deveria ser maior que zero')
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
        self.s.auto_create_nic()
        ifaces = self.s._list_interfaces()
    
    def test_local_dev(self):
        self.s.connect()
        self.s.auto_create_nic()
        iface = self.s.get_netdev('127.0.0.1')
        self.assertEqual(iface.name, 'lo', 'Deveria ser a interface de loopback')
    
    def test_create_route(self):
        self.s.connect()
        self.s.auto_create_nic()
        self.s.create_route('239.0.1.10', 'p7p1')
        self.s.delete_route('239.0.1.10', 'p7p1')
