#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários
"""

from django.test import TestCase
from django.conf import settings

from device.models import *

class CommandsGenerationTest(TestCase):
    def setUp(self):
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='iptv',
            password='iptv',
            offline_mode=True,
        )
        # Input interface
        nic_a = NIC.objects.create(
            server=server,
            name='eth0',
            ipv4='192.168.0.10',
        )
        # Output interface
        nic_b = NIC.objects.create(
            server=server,
            name='eth1',
            ipv4='10.0.1.10',
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
        unicastin = UnicastInput.objects.create(
            server=server,
            interface=nic_a,
            port=30000,
            protocol='udp',
        )
        multicastin = MulticastInput.objects.create(
            server=server,
            interface=nic_a,
            port=40000,
            protocol='udp',
            ip='224.0.0.1',
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
        service_e = DemuxedService.objects.create(
            sid=1,
            sink=unicastin,
        )
        service_f = DemuxedService.objects.create(
            sid=2,
            sink=unicastin,
        )
        service_g = DemuxedService.objects.create(
            sid=1024,
            sink=multicastin,
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
        internal_d = UniqueIP.objects.create(
            port=20000,
            sink=service_e,
            nic=NIC.objects.filter(server=server)[0],
        )
        internal_e = UniqueIP.objects.create(
            port=20000,
            sink=service_f,
            nic=NIC.objects.filter(server=server)[0],
        )
        internal_f = UniqueIP.objects.create(
            port=20000,
            sink=service_g,
            nic=NIC.objects.filter(server=server)[0],
        )
        ipout_a = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.3',
            port=10000,
            protocol='udp',
            interface=nic_b,
            sink=internal_a,
        )
        recorder_a = StreamRecorder.objects.create(
            server=server,
            rotate=60,
            folder='/tmp/recording_a',
            sink=internal_a,
        )
        ipout_b = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.4',
            port=10000,
            protocol='udp',
            interface=nic_b,
            sink=internal_c,
        )
        ipout_c = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.5',
            port=10000,
            protocol='udp',
            interface=nic_b,
            sink=internal_d,
        )
        ipout_d = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.6',
            port=10000,
            protocol='udp',
            interface=nic_b,
            sink=internal_e,
        )
        recorder_a = StreamRecorder.objects.create(
            server=server,
            rotate=60,
            folder='/tmp/recording_b',
            sink=internal_f,
        )
    
    def test_dvbtuner(self):
        tuner = DvbTuner.objects.get(pk=1)
        expected_cmd = (
            "%s "
            "-f 3390000 "
            "-m psk_8 "
            "-s 7400000 "
            "-F 34 "
            "-a 0 "
            "-c %s%d.conf "
            "-r %s%d.sock "
            "&> %s%d.log"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, tuner.pk,
             settings.DVBLAST_SOCKETS_DIR, tuner.pk,
             settings.DVBLAST_LOGS_DIR, tuner.pk,
             )
        self.assertEqual(expected_cmd, tuner._get_cmd(adapter_num=0))
        
        expected_conf = u'239.1.0.2:20000/udp 1 1\n239.1.0.3:20000/udp 1 2\n'
        self.assertEqual(expected_conf, tuner._get_config())
    
    def test_isdbtuner(self):
        tuner = IsdbTuner.objects.get(pk=2)
        expected_cmd = (
            "%s "
            "-f 587143000 "
            "-m qam_auto "
            "-b 6 "
            "-a 1 "
            "-c %s%d.conf "
            "-r %s%d.sock "
            "&> %s%d.log"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, tuner.pk,
             settings.DVBLAST_SOCKETS_DIR, tuner.pk,
             settings.DVBLAST_LOGS_DIR, tuner.pk,
             )
        self.assertEqual(expected_cmd, tuner._get_cmd(adapter_num=1))
        
        expected_conf = u'239.1.0.4:20000/udp 1 1\n'
        self.assertEqual(expected_conf, tuner._get_config())
    
    def test_unicastinput(self):
        unicastin = UnicastInput.objects.get(port=30000)
        expected_cmd = (
            "%s "
            "-D @192.168.0.10:30000/udp "
            "-c %s%d.conf "
            "-r %s%d.sock "
            "&> %s%d.log"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, unicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, unicastin.pk,
             settings.DVBLAST_LOGS_DIR, unicastin.pk,
             )
        self.assertEqual(expected_cmd, unicastin._get_cmd())
        
        expected_conf = u'239.1.0.5:20000/udp 1 1\n239.1.0.6:20000/udp 1 2\n'
        self.assertEqual(expected_conf, unicastin._get_config())
    
    def test_multicastinput(self):
        multicastin = MulticastInput.objects.get(port=40000)
        expected_cmd = (
            "%s "
            "-D @224.0.0.1:40000/udp "
            "-c %s%d.conf "
            "-r %s%d.sock "
            "&> %s%d.log"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, multicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, multicastin.pk,
             settings.DVBLAST_LOGS_DIR, multicastin.pk,
             )
        self.assertEqual(expected_cmd, multicastin._get_cmd())
        
        expected_conf = u'239.1.0.7:20000/udp 1 1024\n'
        self.assertEqual(expected_conf, multicastin._get_config())
    
    def test_multicastoutput(self):
        ipout = MulticastOutput.objects.get(ip_out='239.0.1.3')
        expected_cmd = (
            "%s "
            "-c %s%d.sock "
            "-u @239.1.0.2:20000 "
            "-U 239.0.1.3:10000 "
            "&> %s%d.log"
        ) % (settings.MULTICAT_COMMAND, 
             settings.MULTICAT_SOCKETS_DIR, ipout.pk,
             settings.MULTICAT_LOGS_DIR, ipout.pk,
             )
        self.assertEqual(expected_cmd, ipout._get_cmd())
    
    def test_streamrecorder(self):
        recorder = StreamRecorder.objects.get(folder='/tmp/recording_a')
        expected_cmd = (
            "%s "
            "-r 97200000000 " # 27M * 60 * 60
            "-c %s%d.sock "
            "-u @239.1.0.2:20000 "
            "%s%d "
            "&> %s%d.log"
        ) % (settings.MULTICAT_COMMAND, 
             settings.MULTICAT_SOCKETS_DIR, recorder.pk,
             settings.MULTICAT_RECORDINGS_DIR, recorder.pk,
             settings.MULTICAT_LOGS_DIR, recorder.pk,
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
