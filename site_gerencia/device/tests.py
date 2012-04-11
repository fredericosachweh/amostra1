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
        import getpass
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
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
    
    def tearDown(self):
        Server.objects.all().delete()
    
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
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, tuner.pk,
             settings.DVBLAST_SOCKETS_DIR, tuner.pk,
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
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, tuner.pk,
             settings.DVBLAST_SOCKETS_DIR, tuner.pk,
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
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, unicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, unicastin.pk,
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
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND, 
             settings.DVBLAST_CONFS_DIR, multicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, multicastin.pk,
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
            "-U 239.0.1.3:10000"
        ) % (settings.MULTICAT_COMMAND, 
             settings.MULTICAT_SOCKETS_DIR, ipout.pk,
             )
        self.assertEqual(expected_cmd, ipout._get_cmd())
    
    def test_streamrecorder(self):
        recorder = StreamRecorder.objects.get(folder='/tmp/recording_a')
        expected_cmd = (
            "%s "
            "-r 97200000000 " # 27M * 60 * 60
            "-c %s%d.sock "
            "-u @239.1.0.2:20000 "
            "%s%d"
        ) % (settings.MULTICAT_COMMAND, 
             settings.MULTICAT_SOCKETS_DIR, recorder.pk,
             settings.MULTICAT_RECORDINGS_DIR, recorder.pk,
             )
        self.assertEqual(expected_cmd, recorder._get_cmd())
    
    def test_connections(self):
        # Test dvbtuner generic relation
        dvbtuner = DvbTuner.objects.all()[0]
        dvbtuner_type = ContentType.objects.get_for_model(DvbTuner)
        self.assertItemsEqual(
                    DemuxedService.objects.filter(content_type=dvbtuner_type),
                    dvbtuner.src.all(),
                    )
        # Test unicast input generic relation
        unicastin = UnicastInput.objects.all()[0]
        unicastin_type = ContentType.objects.get_for_model(UnicastInput)
        self.assertItemsEqual(
                    DemuxedService.objects.filter(content_type=unicastin_type),
                    unicastin.src.all(),
                    )
        # Test DemuxedServer and UniqueIP connections
        service = DemuxedService.objects.all()[0]
        internal = UniqueIP.objects.all()[0]
        self.assertEqual(service, internal.sink)
        self.assertEqual(internal, service.src.all()[0])
        # Test connection between internal and output models
        ipout = MulticastOutput.objects.all()[0]
        recorder = StreamRecorder.objects.all()[0]
        internal_src = internal.src
        self.assertIn(ipout, internal_src)
        self.assertIn(recorder, internal_src)
        self.assertEqual(internal, ipout.sink)
        self.assertEqual(internal, recorder.sink)

class GenericSourceTest(TestCase):

    def test_vlc_source(self):
        import getpass
        s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa'
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
        ip.save()
        nip = UniqueIP.objects.get(content_type=ip.content_type.id,
            object_id=vlc.pk)
        nip.sink.start()
        nip.sink.stop()

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
        import os
        import getpass
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 22
        srv.username = getpass.getuser()
        srv.rsakey = '~/.ssh/id_rsa'
        srv.connect()
        ret = srv.execute('/bin/pwd')
        self.assertEqual(
            ret[0],
            '%s\n' % (os.environ.get('HOME')),
            'O home deveria ser "%s\n"' % (os.environ.get('HOME'))
        )
    
    def test_connection_failure(self):
        "Teste para conectar e falhar uma conexão (Porta errada)"
        import getpass
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 2222
        srv.username = getpass.getuser()
        srv.rsakey = '~/.ssh/id_rsa'
        srv.connect()
        self.assertEqual(str(srv.msg),
            'Unable to connect to 127.0.0.1: [Errno 111] Connection refused',
            'Deveria dar erro de conexão')
        self.assertFalse(srv.status, 'O status da conexão deveria ser False')
    
    def test_low_respose_command(self):
        "Test de comando demorado para executar"
        import os
        import getpass
        from lib.ssh import Connection
        conn = Connection('127.0.0.1',
            username=getpass.getuser(), private_key='~/.ssh/id_rsa')
        test_command = '%s/device/helper/test' % (os.path.abspath('.'))
        t = conn.execute_with_timeout(test_command,timeout=2)
        self.assertEqual(
            'Inicio\nP1**********Fim',
            t,
            'Valor esperado diferente [%s]' % t
        )

class ServerTest(TestCase):
    
    def setUp(self):
        import getpass
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
        )
    
    def test_list_dir(self):
        server = Server.objects.get(pk=1)
        l = server.list_dir('/')
        self.assertGreater( l.count('boot') , 0 ,
            'Deveria existir o diretório boot')
        self.assertGreater( l.count('bin') , 0 ,
            'Deveria existir o diretório bin')
        self.assertGreater( l.count('usr') , 0 ,
            'Deveria existir o diretório usr')
    
    def test_list_process(self):
        from models import Server
        server = Server.objects.get(pk=1)
        server.connect()
        procs = server.list_process()
        self.assertEqual(procs[0]['pid'],
            1,
            'O primero processo deveria ter pid=1')
    
    def test_start_process(self):
        server = Server.objects.get(pk=1)
        cmd = '/bin/sleep 10'
        pid = server.execute_daemon(cmd)
        self.assertTrue(server.process_alive(pid),
            'O processo pid=%d deveria estar vivo.' % pid)
        self.assertGreater(pid, 0, 'O processo deveria ser maior que zero')
        server.kill_process(pid)
        self.assertFalse(server.process_alive(pid),
            'O processo pid=%d deveria ter morrido.' % pid)
    
    def test_list_ifaces(self):
        server = Server.objects.get(pk=1)
        server.connect()
        server.auto_create_nic()
        ifaces = server._list_interfaces()
    
    def test_local_dev(self):
        server = Server.objects.get(pk=1)
        server.connect()
        server.auto_create_nic()
        iface = server.get_netdev('127.0.0.1')
        self.assertEqual(iface, 'lo', 'Deveria ser a interface de loopback')
    
    def test_create_route(self):
        server = Server.objects.get(pk=1)
        server.connect()
        server.auto_create_nic()
        route = ('239.0.1.10', 'lo')
        
        server.create_route(*route)
        routes = server.list_routes()
        self.assertIn(route, routes,
                'Route %s -> %s should exists' % route)
        
        server.delete_route(*route)
        routes = server.list_routes()
        self.assertNotIn(route, routes,
                'Route %s -> %s should not exists' % route)
