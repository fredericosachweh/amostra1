'<option value="2">bar0 - 172.17.0.2</option>'#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários
"""

from django.test import TestCase
from django.test import LiveServerTestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.conf import settings

from device.models import *

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


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
        dvbworld = DigitalTunerHardware.objects.create(
            server=server,
            uniqueid='00:00:00:00:00:00',
            adapter_nr=0,
        )
        dvbtuner = DvbTuner.objects.create(
            server=server,
            antenna=antenna,
            frequency=3990,
            symbol_rate=7400,
            modulation='8PSK',
            polarization='H',
            fec='34',
            adapter=dvbworld.uniqueid,
        )
        pixelview = DigitalTunerHardware.objects.create(
            server=server,
            adapter_nr=1,
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
        fileinput = FileInput.objects.create(
            server=server,
            filename='foobar.mkv',
        )
        service_a = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=dvbtuner,
        )
        service_b = DemuxedService.objects.create(
            server=server,
            sid=2,
            sink=dvbtuner,
        )
        service_c = DemuxedService.objects.create(
            server=server,
            sid=3,
            sink=dvbtuner,
        )
        service_d = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=isdbtuner,
        )
        service_e = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
        )
        service_f = DemuxedService.objects.create(
            server=server,
            sid=2,
            sink=unicastin,
        )
        service_g = DemuxedService.objects.create(
            server=server,
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
        internal_g = UniqueIP.objects.create(
            port=20000,
            sink=fileinput,
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
            keep_time=168
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
        recorder_b = StreamRecorder.objects.create(
            server=server,
            rotate=60,
            folder='/tmp/recording_b',
            sink=internal_f,
            keep_time=130,
        )
        ipout_e = MulticastOutput.objects.create(
            server=server,
            ip_out='239.0.1.7',
            port=10000,
            protocol='udp',
            interface=nic_b,
            sink=internal_g,
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
        self.assertEqual(expected_cmd, tuner._get_cmd())
        # Workaround: this should be done inside the start method
        for service in tuner.src.all():
            service.enabled = True
            service.save()
        
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
        for service in tuner.src.all():
            service.enabled = True
            service.save()

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
        for service in unicastin.src.all():
            service.enabled = True
            service.save()

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
        for service in multicastin.src.all():
            service.enabled = True
            service.save()

        expected_conf = u'239.1.0.7:20000/udp 1 1024\n'
        self.assertEqual(expected_conf, multicastin._get_config())

    def test_demuxedinput(self):
        unicastin = UnicastInput.objects.get(port=30000)
        self.assertFalse(unicastin.running())
        services = unicastin.src.all()
        service_a = services[0]
        service_b = services[1]
        
        

    def test_fileinput(self):
        fileinput = FileInput.objects.all()[0]
        expected_cmd = (
            '%s '
            '-I dummy -v -R '
            '"foobar.mkv" '
            '--sout "#std{access=udp,mux=ts,dst=239.1.0.8:20000}"'
        ) % (settings.VLC_COMMAND)
        self.assertEqual(expected_cmd, fileinput._get_cmd())

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
        folder='/tmp/recording_a'
        recorder = StreamRecorder.objects.get(folder=folder)
        expected_cmd = (
            "%s "
            "-r 97200000000 " # 27M * 60 * 60
            "-c %s%d.sock "
            "-u @239.1.0.2:20000 "
            "%s/%d"
        ) % (settings.MULTICAT_COMMAND,
             settings.MULTICAT_SOCKETS_DIR, recorder.pk,
             folder, recorder.pk,
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


class AdaptersManipulationTests(TestCase):
    def setUp(self):
        import getpass
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
        )
        self.client = Client()
        self.factory = RequestFactory()

    def tearDown(self):
        Server.objects.all().delete()

    def test_update_by_post(self):
        # Create a new adapter
        response = self.client.post(
            reverse('server_adapter_add'), {'adapter_nr' : 0})
        self.assertEqual(response.status_code, 200)
        # Delete it
        response = self.client.post(
            reverse('server_adapter_remove'), {'adapter_nr' : 0})
        self.assertEqual(response.status_code, 200)

    def test_isdb_adapter_nr(self):
        server = Server.objects.get(pk=1)
        DigitalTunerHardware.objects.create(
            server=server,
            adapter_nr=2,
            id_vendor='1554',
        )
        DigitalTunerHardware.objects.create(
            server=server,
            adapter_nr=4,
            id_vendor='1554',
        )
        isdbtuner_a = IsdbTuner.objects.create(
            server=server,
            frequency=569143,
        )
        isdbtuner_b = IsdbTuner.objects.create(
            server=server,
            frequency=575143,
        )
        isdbtuner_c = IsdbTuner.objects.create(
            server=server,
            frequency=587143,
        )
        # Takes the first adapter
        isdbtuner_a.start()
        self.assertEqual(2, isdbtuner_a.adapter)
        # Takes the second
        isdbtuner_b.start()
        self.assertEqual(4, isdbtuner_b.adapter)
        # This will raise an exception because there's no adapters left
        self.assertRaises(IsdbTuner.AdapterNotInstalled, isdbtuner_c.start)


class MySeleniumTests(LiveServerTestCase):
    fixtures = ['user-data.json', 'default-server.json',
                'antenna.json', 'dvbworld.json', 'pixelview.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(MySeleniumTests, cls).tearDownClass()
        cls.selenium.quit()

    def _login(self, username, password):
        login_url = '%s%s' % (self.live_server_url,
                                reverse('django.contrib.auth.views.login'))
        self.selenium.get(login_url)
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_tag_name('body'))

    def _is_logged(self):
        from django.contrib.auth.models import User
        from django.contrib.sessions.models import Session
        from datetime import datetime
        admin = User.objects.get(username='admin')
        # Query all non-expired sessions
        sessions = Session.objects.filter(expire_date__gte=datetime.now())
        for session in sessions:
            data = session.get_decoded()
            if data.get('_auth_user_id', None) == admin.id:
                return True
        return False

    def _select(self, id, choice):
        field = self.selenium.find_element_by_id(id)
        for option in field.find_elements_by_tag_name('option'):
            if option.text == choice:
                option.click() # select() in earlier versions of webdriver

    def _select_by_value(self, id, value):
        field = self.selenium.find_element_by_id(id)
        field.find_element_by_xpath("//option[@value='%s']" % value).click()

    def test_valid_login(self):
        self.assertFalse(self._is_logged())
        self._login('admin', 'cianet')
        index_url = '%s%s' % (self.live_server_url, reverse('admin:index'))
        self.assertEqual(index_url, self.selenium.current_url,
                         "Could not login")
        self.assertTrue(self._is_logged())

    def test_invalid_login(self):
        self._login('admin', 'cianet123')
        login_url = '%s%s' % (self.live_server_url,
                                reverse('django.contrib.auth.views.login'))
        self.assertEqual(login_url, self.selenium.current_url,
                         "Login should have failed")

    def test_unicastinput(self):
        fields = {'server' : 'local',
                  'interface' : 1,
        }
        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:device_unicastinput_add'))
        self.selenium.get(add_new_url)
        #self._select('id_server', 'local')
        self._select_by_value('id_server', 1)
        # Wait ajax to complete
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_xpath("//option[@value='2']"))
        self._select('id_interface', 'eth0 - 192.168.0.14')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_tag_name('body'))
        unicastin = UnicastInput.objects.get(pk=1)
        self.assertEqual(1, unicastin.server_id)
        self.assertEqual(10000, unicastin.port)
        self.assertEqual('192.168.0.14', unicastin.interface.ipv4)
        self.assertEqual('udp', unicastin.protocol)
        unicastin.delete()

    def test_multicastinput(self):
        import getpass
        myuser = getpass.getuser()
        servers = Server.objects.all()
        servers.update(username=myuser)

        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:device_multicastinput_add'))
        self.selenium.get(add_new_url)
        self._select('id_server', 'local')
        self._select('id_interface', 'lo - 127.0.0.1')
        ip = self.selenium.find_element_by_name("ip")
        ip.send_keys('239.0.1.1')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_tag_name('body'))
        multicastin = MulticastInput.objects.get(pk=1)
        self.assertEqual(1, multicastin.server_id)
        self.assertEqual(10000, multicastin.port)
        self.assertEqual('127.0.0.1', multicastin.interface.ipv4)
        self.assertEqual('udp', multicastin.protocol)
        self.assertEqual('239.0.1.1', multicastin.ip)
        multicastin.delete()

    def test_dvbtuner(self):
        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:device_dvbtuner_add'))
        self.selenium.get(add_new_url)
        self._select('id_server', 'local')
        freq = self.selenium.find_element_by_name("frequency")
        freq.send_keys('3990')
        sr = self.selenium.find_element_by_name("symbol_rate")
        sr.send_keys('7400')
        self._select('id_modulation', '8-PSK')
        self._select('id_polarization', 'Vertical (V)')
        self._select('id_fec', '3/4')
        self._select('id_adapter', 'DVBWorld 00:00:00:00:00:00')
        self._select('id_antenna', 'C2')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_tag_name('body'))
        tuner = DvbTuner.objects.get(pk=1)
        self.assertEqual(3990, tuner.frequency)
        self.assertEqual(7400, tuner.symbol_rate)
        self.assertEqual('8PSK', tuner.modulation)
        self.assertEqual('V', tuner.polarization)
        self.assertEqual(1, tuner.antenna.pk)
        self.assertEqual('34', tuner.fec)
        self.assertEqual('00:00:00:00:00:00', tuner.adapter)
        tuner.delete()

    def test_isdbtuner(self):
        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:device_isdbtuner_add'))
        self.selenium.get(add_new_url)
        self._select('id_server', 'local')
        freq = self.selenium.find_element_by_name("frequency")
        freq.send_keys('587143')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_tag_name('body'))
        tuner = IsdbTuner.objects.get(pk=1)
        self.assertEqual(587143, tuner.frequency)
        self.assertEqual('qam', tuner.modulation)
        self.assertEqual(6, tuner.bandwidth)
        tuner.delete()

class UniqueIPTest(TestCase):

    def test_sequential(self):
        srv = Server.objects.create(host='127.0.0.1', name='local',
            ssh_port=22)
        nic = NIC.objects.create(server=srv, ipv4='127.0.0.1')
        for i in range(1024):
            ip1 = UniqueIP(nic=nic)
            ip1.save()


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
        t = conn.execute_with_timeout(test_command, timeout=2)
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
        self.client = Client()

    def test_list_dir(self):
        server = Server.objects.get(pk=1)
        l = server.list_dir('/')
        self.assertGreater(l.count('boot'), 0,
            'Deveria existir o diretório boot')
        self.assertGreater(l.count('bin'), 0,
            'Deveria existir o diretório bin')
        self.assertGreater(l.count('usr'), 0,
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

    def test_list_interfaces_view(self):
        server = Server.objects.get(pk=1)
        NIC.objects.create(
            server=server,
            ipv4='192.168.0.10',
            name='foo0'
        )
        NIC.objects.create(
            server=server,
            ipv4='172.17.0.2',
            name='bar0'
        )
        url = reverse('device.views.server_list_interfaces') + '?server=1'
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        expected = '<option selected="selected" value="">---------</option>'
        self.assertIn(expected, response.content)
        pk = NIC.objects.get(server=server, name='foo0').pk
        expected = '<option value="%d">foo0 - 192.168.0.10</option>' % pk
        self.assertIn(expected, response.content)
        pk = NIC.objects.get(server=server, name='bar0').pk
        expected = '<option value="%d">bar0 - 172.17.0.2</option>' % pk
        self.assertIn(expected, response.content)

    def test_dvbtuners_list_view(self):
        url = reverse('device.views.server_list_dvbadapters')
        server = Server.objects.get(pk=1)
        dvbworld = DigitalTunerHardware.objects.create(
            server=server,
            uniqueid='00:00:00:00:00:00',
            id_vendor='04b4',
            id_product='2104',
            adapter_nr=0,
        )
        DigitalTunerHardware.objects.create(
            server=server,
            uniqueid='00:00:00:00:00:01',
            id_vendor='04b4',
            id_product='2104',
            adapter_nr=1,
        )
        DigitalTunerHardware.objects.create(
            server=server,
            uniqueid='00:00:00:00:00:02',
            id_vendor='04b4',
            id_product='2104',
            adapter_nr=2,
        )
        expected = '<option value="">---------</option>' \
                   '<option value="00:00:00:00:00:00">' \
                   'DVBWorld 00:00:00:00:00:00</option>' \
                   '<option value="00:00:00:00:00:01">' \
                   'DVBWorld 00:00:00:00:00:01</option>' \
                   '<option value="00:00:00:00:00:02">' \
                   'DVBWorld 00:00:00:00:00:02</option>'
        response = self.client.get(url + '?server=%d&type=dvb' % server.pk)
        # Without any DvbTuner created
        self.assertEqual(expected, response.content)

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
            adapter=dvbworld.uniqueid,
        )
        # Editing a created DvbTuner
        response = self.client.get(url + '?server=%d&tuner=1&type=dvb'
            % server.pk)
        self.assertEqual(expected, response.content)

        expected = '<option value="">---------</option>' \
                   '<option value="00:00:00:00:00:01">' \
                   'DVBWorld 00:00:00:00:00:01</option>' \
                   '<option value="00:00:00:00:00:02">' \
                   'DVBWorld 00:00:00:00:00:02</option>'
        response = self.client.get(url + '?server=%d&type=dvb' % server.pk)
        # With one created DvbTuner, while inserting another one
        self.assertEqual(expected, response.content,
            'The already used adapter should have been excluded')

    def test_available_isdbtuners_view(self):
        url = reverse('device.views.server_available_isdbtuners')
        server = Server.objects.get(pk=1)
        # No installed adapters
        response = self.client.get(url + '?server=%d' % server.pk)
        self.assertEqual('0', response.content)

        DigitalTunerHardware.objects.create(
            server=server,
            id_vendor='1554',
            id_product='5010',
            adapter_nr=0,
        )
        DigitalTunerHardware.objects.create(
            server=server,
            id_vendor='1554',
            id_product='5010',
            adapter_nr=1,
        )

        # Without any IsdbTuner created
        response = self.client.get(url + '?server=%d' % server.pk)
        self.assertEqual('2', response.content)

        IsdbTuner.objects.create(
            server=server,
            frequency=587143,
            bandwidth=6,
            modulation='qam',
        )

        # While editing a created IsdbTuner
        response = self.client.get(url + '?server=%d&tuner=1' % server.pk)
        self.assertEqual('2', response.content)

        # Creating a new one
        response = self.client.get(url + '?server=%d' % server.pk)
        self.assertEqual('1', response.content)


class TestViews(TestCase):
    """
    Unit test for device views
    """

    def setUp(self):
        import getpass
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
            offline_mode=False,
        )
        # Input interface
        NIC.objects.create(
            server=server,
            name='foobar0',
            ipv4='192.168.0.10',
        )
        # Output interface
        NIC.objects.create(
            server=server,
            name='foobar1',
            ipv4='10.0.1.10',
        )

    def test_server_status(self):
        server = Server.objects.get(pk=1)
        c = Client()
        url = reverse('device.views.server_status', kwargs={'pk':server.pk})
        response = c.get(url, follow=True)
        self.assertRedirects(response,
            'http://testserver/tv/administracao/device/server/', 302)
        urlnotfound = reverse('device.views.server_status', kwargs={'pk':2})
        response = c.get(urlnotfound, follow=True)
        self.assertEqual(response.status_code, 404, 'Deveria ser 404')

    def test_fileinput_scanfolder(self):
        import re
        server = Server.objects.get(pk=1)
        # Create a temporary file inside the videos folder
        out = server.execute('/bin/mktemp -p %s' % settings.VLC_VIDEOFILES_DIR)
        # Make sure the file name is returned on the list
        url = reverse('device.views.server_fileinput_scanfolder')
        response = self.client.get(url + '?server=%d' % server.pk)
        options = unicode(response.content, 'utf-8').split(u'\n')
        full_path = u" ".join(out).strip()
        match = re.match(r'^%s(.*)$' %
            re.escape(settings.VLC_VIDEOFILES_DIR), full_path)
        file_name = match.groups(0)[0]
        expected = u'<option value="%s">%s</option>' % (
            full_path, file_name)
        server.execute('/bin/rm -f %s' % full_path)
        self.assertIn(expected, options)


class TestRecord(TestCase):
    """
    Test record stream on remote server
    """

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
        NIC.objects.create(
            server=server,
            name='eth0',
            ipv4='192.168.0.10',
        )
        NIC.objects.create(
            server=server,
            name='eth1',
            ipv4='10.0.1.10',
        )

    def test_record(self):
        srv = Server.objects.get(name='local')
        ext_ip = UniqueIP.objects.create(
            port=20000,
            nic=NIC.objects.filter(server=srv)[0],
        )
        ext_ip.ip = '127.0.0.1'
        ext_ip.save()
        recorder = StreamRecorder.objects.create(
            server=srv,
            rotate=60,
            folder='/tmp/recording_xx',
            keep_time=130,
            sink=ext_ip,
        )
        cmd_expected = '%s \
-r %d -c %s%d.sock -u @127.0.0.1:20000 /tmp/recording_xx/%d' % (
            settings.MULTICAT_COMMAND,
            (60*60*27000000),
            settings.MULTICAT_SOCKETS_DIR,
            recorder.pk,
            recorder.pk,
            )
        self.assertEqual(recorder._get_cmd(), cmd_expected,
            'Comando de gravação difere do esperado')

