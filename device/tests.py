#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários
"""

from django.test import TestCase
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from django.test.client import Client
from django.test.client import RequestFactory
from django.conf import settings

from device.models import *

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from tv.models import Channel
## import getpass
## getpass.getuser() -> 'nginx'


@override_settings(DVBLAST_COMMAND=settings.DVBLAST_DUMMY)
@override_settings(DVBLASTCTL_COMMAND=settings.DVBLASTCTL_DUMMY)
@override_settings(MULTICAT_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(MULTICATCTL_COMMAND=settings.MULTICATCTL_DUMMY)
@override_settings(VLC_COMMAND=settings.VLC_DUMMY)
class CommandsGenerationTest(TestCase):
    def setUp(self):
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa',
        )
        nic = NIC.objects.get(ipv4='127.0.0.1')
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
        DigitalTunerHardware.objects.create(
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
            interface=nic,
            port=30000,
            protocol='udp',
        )
        multicastin = MulticastInput.objects.create(
            server=server,
            interface=nic,
            port=40000,
            protocol='udp',
            ip='224.0.0.1',
        )
        fileinput = FileInput.objects.create(
            server=server,
            filename='foobar.mkv',
            nic_src=nic,
        )
        fi_soft_transcoder = FileInput.objects.create(
            server=server,
            filename='foobar.mkv',
            nic_src=nic,
        )
        service_a = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=dvbtuner,
            nic_src=nic,
        )
        service_b = DemuxedService.objects.create(
            server=server,
            sid=2,
            sink=dvbtuner,
            nic_src=nic,
        )
        DemuxedService.objects.create(
            server=server,
            sid=3,
            sink=dvbtuner,
            nic_src=nic,
        )
        service_d = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=isdbtuner,
            nic_src=nic,
        )
        service_e = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )
        service_f = DemuxedService.objects.create(
            server=server,
            sid=2,
            sink=unicastin,
            nic_src=nic,
        )
        service_g = DemuxedService.objects.create(
            server=server,
            sid=1024,
            sink=multicastin,
            nic_src=nic,
        )
        internal_a = UniqueIP.objects.create(
            port=20000,
            sink=service_a,
        )
        UniqueIP.objects.create(
            port=20000,
            sink=service_b,
        )
        internal_c = UniqueIP.objects.create(
            port=20000,
            sink=service_d,
        )
        internal_d = UniqueIP.objects.create(
            port=20000,
            sink=service_e,
        )
        internal_e = UniqueIP.objects.create(
            port=20000,
            sink=service_f,
        )
        internal_f = UniqueIP.objects.create(
            port=20000,
            sink=service_g,
        )
        internal_g = UniqueIP.objects.create(
            port=20000,
            sink=fileinput,
        )
        file_to_soft = UniqueIP.objects.create(
            port=20000,
            sink=fi_soft_transcoder,
        )
        soft_transcoder = SoftTranscoder.objects.create(
            server=server,
            sink=file_to_soft,
            nic_sink=nic,
            nic_src=nic,
        )
        soft_to_ipout = UniqueIP.objects.create(
            port=20000,
            sink=soft_transcoder,
        )
        MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            port=10000,
            protocol='udp',
            interface=nic,
            sink=internal_a,
            nic_sink=nic,
        )
        storage1 = Storage.objects.create(
            folder='/tmp/recording_1',
            server=server,
            )
        StreamRecorder.objects.create(
            server=server,
            storage=storage1,
            rotate=60,
            sink=internal_a,
            keep_time=168,
            nic_sink=nic,
        )
        MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.4',
            port=10000,
            protocol='udp',
            interface=nic,
            sink=internal_c,
            nic_sink=nic,
        )
        MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.5',
            port=10000,
            protocol='udp',
            interface=nic,
            sink=internal_d,
            nic_sink=nic,
        )
        MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.6',
            port=10000,
            protocol='udp',
            interface=nic,
            sink=internal_e,
            nic_sink=nic,
        )
        StreamRecorder.objects.create(
            server=server,
            storage=storage1,
            rotate=60,
            sink=internal_f,
            keep_time=130,
            nic_sink=nic,
        )
        MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.7',
            port=10000,
            protocol='udp',
            interface=nic,
            sink=internal_g,
            nic_sink=nic,
        )
        MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.8',
            port=10000,
            protocol='udp',
            interface=nic,
            sink=soft_to_ipout,
            nic_sink=nic,
        )
        # TODO - FileInput -> UniqueIP -> SoftTranscoder \
        #-> UniqueIP -> MulticastOutput

    def tearDown(self):
        Server.objects.all().delete()

    def test_dvbtuner(self):
        self.maxDiff = None
        tuner = DvbTuner.objects.get(pk=1)
        expected_cmd = unicode(
            "%s "
            "-f 3390000 "
            "-m psk_8 "
            "-s 7400000 "
            "-F 34 "
            "-a 0 "
            "-w "
            "-c %s%d.conf "
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND,
             settings.DVBLAST_CONFS_DIR, tuner.pk,
             settings.DVBLAST_SOCKETS_DIR, tuner.pk,
             )
        self.assertEqual(expected_cmd, tuner._get_cmd())

        tuner.start()
        self.assertTrue(tuner.running())
        self.assertTrue(tuner.status)

        tuner.start_all_services()
        for service in tuner._list_all_services():
            self.assertTrue(service.status)

        expected_conf = u'239.10.0.2:20000@127.0.0.1/udp 1 1\n\
239.10.0.3:20000@127.0.0.1/udp 1 2\n'
        self.assertEqual(expected_conf, tuner._get_config())

        tuner.stop()
        self.assertFalse(tuner.running())
        self.assertFalse(tuner.status)

        for service in tuner._list_all_services():
            self.assertFalse(service.status)

    def test_isdbtuner(self):
        tuner = IsdbTuner.objects.get(pk=2)
        expected_cmd = unicode(
            "%s "
            "-f 587143000 "
            "-m qam_auto "
            "-b 6 "
            "-a 1 "
            "-w "
            "-c %s%d.conf "
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND,
             settings.DVBLAST_CONFS_DIR, tuner.pk,
             settings.DVBLAST_SOCKETS_DIR, tuner.pk,
             )
        self.assertEqual(expected_cmd, tuner._get_cmd(adapter_num=1))

        tuner.start(adapter_num=1)
        self.assertTrue(tuner.running())
        self.assertTrue(tuner.status)

        tuner.start_all_services()
        for service in tuner._list_all_services():
            self.assertTrue(service.status)

        expected_conf = u'239.10.0.4:20000@127.0.0.1/udp 1 1\n'
        self.assertEqual(expected_conf, tuner._get_config())

        tuner.stop()
        self.assertFalse(tuner.running())
        self.assertFalse(tuner.status)

        for service in tuner._list_all_services():
            self.assertFalse(service.status)

    def test_unicastinput(self):
        unicastin = UnicastInput.objects.get(port=30000)
        expected_cmd = unicode(
            "%s "
            "-D @127.0.0.1:30000/udp "
            "-c %s%d.conf "
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND,
             settings.DVBLAST_CONFS_DIR, unicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, unicastin.pk,
             )
        self.assertEqual(expected_cmd, unicastin._get_cmd())

        unicastin.start()
        self.assertTrue(unicastin.running())
        self.assertTrue(unicastin.status)

        unicastin.start_all_services()
        for service in unicastin._list_all_services():
            self.assertTrue(service.status)

        expected_conf = u'239.10.0.5:20000@127.0.0.1/udp 1 \
1\n239.10.0.6:20000@127.0.0.1/udp 1 2\n'
        self.assertEqual(expected_conf, unicastin._get_config())

        unicastin.stop()
        self.assertFalse(unicastin.running())
        self.assertFalse(unicastin.status)

        for service in unicastin._list_all_services():
            self.assertFalse(service.status)

    def test_multicastinput(self):
        multicastin = MulticastInput.objects.get(port=40000)
        expected_cmd = unicode(
            "%s "
            "-D @224.0.0.1:40000/udp "
            "-c %s%d.conf "
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND,
             settings.DVBLAST_CONFS_DIR, multicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, multicastin.pk,
             )
        self.assertEqual(expected_cmd, multicastin._get_cmd())

        multicastin.start()
        self.assertTrue(multicastin.running())
        self.assertTrue(multicastin.status)

        multicastin.start_all_services()
        for service in multicastin._list_all_services():
            self.assertTrue(service.status)

        expected_conf = u'239.10.0.7:20000@127.0.0.1/udp 1 1024\n'
        self.assertEqual(expected_conf, multicastin._get_config())

        multicastin.stop()
        self.assertFalse(multicastin.running())
        self.assertFalse(multicastin.status)

        for service in multicastin._list_all_services():
            self.assertFalse(service.status)

    def test_demuxedinput(self):
        r"""When starting a demuxedinput the
           connected device should start as well"""
        unicastin = UnicastInput.objects.get(port=30000)
        self.assertFalse(unicastin.running())

        services = unicastin._list_all_services()
        if len(services) > 0:
            service = services[0]
        else:
            self.fail("There is no service attached to this device")
        # TODO: coerência entre banco e instância
        service.start()
        # recarregando o banco porque o unicastin atual esta diferente do banco
        unicastin = UnicastInput.objects.get(port=30000)
        self.assertTrue(service.running())
        self.assertTrue(unicastin.running())

        unicastin.stop()
        # recarregando o banco porque o service atual esta diferente do banco
        service = DemuxedService.objects.get(pk=service.pk)
        self.assertFalse(unicastin.running())
        self.assertFalse(service.running())

    def test_fileinput(self):
        fileinput = FileInput.objects.all()[0]
        expected_cmd = unicode(
            '%s '
            '-I dummy -v -R '
            '"foobar.mkv" '
            '--miface lo '
            '--sout "#std{access=udp,mux=ts,dst=239.10.0.8:20000}"'
        ) % (settings.VLC_COMMAND)
        self.assertEqual(expected_cmd, fileinput._get_cmd())

        fileinput.start()
        self.assertTrue(fileinput.running())

        fileinput.stop()
        self.assertFalse(fileinput.running())

    def test_multicastoutput(self):
        ipout = MulticastOutput.objects.get(ip='239.0.1.3')
        expected_cmd = unicode(
            "%s "
            "-c %s%d.sock "
            "-u @239.10.0.2:20000/ifaddr=127.0.0.1 "
            "-U 239.0.1.3:10000@127.0.0.1"
        ) % (settings.MULTICAT_COMMAND,
             settings.MULTICAT_SOCKETS_DIR, ipout.pk,
             )
        self.assertEqual(expected_cmd, ipout._get_cmd())

        ipout.start()
        self.assertTrue(ipout.running())

        ipout.stop()
        self.assertFalse(ipout.running())

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

    def test_soft_transcoder(self):
        soft_transcoder = SoftTranscoder.objects.all()[0]
        # Multicast input
        expected_cmd = unicode(
            "%s "
            "-I dummy "
            "--miface lo "
            "--sout=\"#std{access=udp,mux=ts,bind=127.0.0.1,"
            "dst=239.10.0.10:20000}\" "
            "udp://@239.10.0.9:20000/ifaddr=127.0.0.1"
        ) % settings.VLC_COMMAND
        self.assertEqual(expected_cmd, soft_transcoder._get_cmd())
        # Unicast input
        soft_transcoder.sink.ip = '192.169.1.100'
        expected_cmd = unicode(
            "%s "
            "-I dummy "
            "--miface lo "
            "--sout=\"#std{access=udp,mux=ts,bind=127.0.0.1,"
            "dst=239.10.0.10:20000}\" "
            "udp://@127.0.0.1:20000"
        ) % settings.VLC_COMMAND
        self.assertEqual(expected_cmd, soft_transcoder._get_cmd())
        # Enable audio transcoding
        soft_transcoder.sink.ip = '239.10.0.9'
        soft_transcoder.transcode_audio = True
        soft_transcoder.audio_codec = 'mp4a'
        expected_cmd = unicode(
            "%s "
            "-I dummy "
            "--miface lo "
            "--sout=\"#transcode{acodec=mp4a,ab=96,afilter={}}"
            ":std{access=udp,mux=ts,bind=127.0.0.1,dst=239.10.0.10:20000}\" "
            "udp://@239.10.0.9:20000/ifaddr=127.0.0.1"
        ) % settings.VLC_COMMAND
        self.assertEqual(expected_cmd, soft_transcoder._get_cmd())
        # Enable audio filters
        soft_transcoder.sync_on_audio_track = True
        soft_transcoder.apply_gain = True
        soft_transcoder.apply_compressor = True
        soft_transcoder.apply_normvol = True
        expected_cmd = unicode(
            "%s "
            "-I dummy "
            "--miface lo "
            "--sout-transcode-audio-sync "
            "--gain-value 1.00 "
            "--compressor-rms-peak 0.00 "
            "--compressor-attack 25.00 "
            "--compressor-release 100.00 "
            "--compressor-threshold -11.00 "
            "--compressor-ratio 8.00 "
            "--compressor-knee 2.50 "
            "--compressor-makeup-gain 7.00 "
            "--norm-buff-size 20 "
            "--norm-max-level 2.00 "
            "--sout=\"#transcode{acodec=mp4a,ab=96,afilter={gain:compressor:"
            "volnorm}}"
            ":std{access=udp,mux=ts,bind=127.0.0.1,dst=239.10.0.10:20000}\" "
            "udp://@239.10.0.9:20000/ifaddr=127.0.0.1"
        ) % settings.VLC_COMMAND

        self.assertEqual(expected_cmd, soft_transcoder._get_cmd())
        soft_transcoder.start()
        self.assertTrue(soft_transcoder.running())

        soft_transcoder.stop()
        self.assertFalse(soft_transcoder.running())


class AdaptersManipulationTests(TestCase):

    def setUp(self):
        import getpass
        Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa',
        )
        self.client = Client()
        self.factory = RequestFactory()

    def tearDown(self):
        Server.objects.all().delete()

    def test_update_by_post(self):
        # Create a new adapter
        response = self.client.post(
            reverse('server_adapter_add', kwargs={'pk': 1, 'action': 'add'}),
            {'adapter_nr': 'dvb0.frontend0'})
        self.assertEqual(response.status_code, 200)
        # Delete it
        response = self.client.post(
            reverse('server_adapter_remove', kwargs={'pk': 1}),
            {'adapter_nr': 'dvb0.frontend0'})
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
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

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

    def _select(self, el_id, choice):
        field = self.selenium.find_element_by_id(el_id)
        for option in field.find_elements_by_tag_name('option'):
            if option.text == choice:
                option.click()  # select() in earlier versions of webdriver

    def _select_by_value(self, el_id, value):
        field = self.selenium.find_element_by_id(el_id)
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
        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
            reverse('admin:device_unicastinput_add'))
        self.selenium.get(add_new_url)
        self._select_by_value('id_server', 1)
        nics = NIC.objects.all()
        # Wait ajax to complete
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_xpath(
                "//option[@value='2']"))
        self._select('id_interface', '%s' % nics[1])
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
        myuser = 'nginx'
        servers = Server.objects.all()
        servers.update(username=myuser)

        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:device_multicastinput_add'))
        self.selenium.get(add_new_url)
        self._select('id_server', 'local')
        nic = servers[0].nic_set.all()[0]
        self._select('id_interface', '%s' % nic)
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
        srv.username = 'nginx'
        srv.rsakey = '~/.ssh/id_rsa'
        srv.connect()
        ret = srv.execute('/bin/pwd')
        self.assertEqual(
            ret[0],
            '/iptv/var/lib/nginx\n',
            'O home deveria ser "/iptv/var/lib/nginx\n"'
        )

    def test_connection_failure(self):
        "Teste para conectar e falhar uma conexão (Porta errada)"
        import getpass
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 2222
        srv.username = 'nginx'
        srv.rsakey = '~/.ssh/id_rsa'
        srv.connect()
        self.assertEqual(str(srv.msg),
            'Unable to connect to 127.0.0.1: [Errno 111] Connection refused',
            'Deveria dar erro de conexão')
        self.assertFalse(srv.status, 'O status da conexão deveria ser False')


class ServerTest(TestCase):

    def setUp(self):
        import getpass
        Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
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
        nic0 = NIC.objects.get(server=server, name='foo0')
        expected = '<option value="%d">%s</option>' % (nic0.pk, nic0)
        self.assertIn(expected, response.content)
        nic1 = NIC.objects.get(server=server, name='bar0')
        expected = '<option value="%d">%s</option>' % (nic1.pk, nic1)
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
        expected = '<option value="">---------</option>'\
        '<option value="00:00:00:00:00:00">00:00:00:00:00:00 ( - 04b4:2104)'\
        '</option>'\
        '<option value="00:00:00:00:00:01">00:00:00:00:00:01 ( - 04b4:2104)'\
        '</option>'\
        '<option value="00:00:00:00:00:02">00:00:00:00:00:02 ( - 04b4:2104)'\
        '</option>'
        response = self.client.get(url + '?server=%d&type=dvb' % server.pk)
        # Without any DvbTuner created
        self.assertEqual(expected, response.content)

        antenna = Antenna.objects.create(
            satellite='StarOne C2',
            lnb_type='multiponto_c',
        )
        DvbTuner.objects.create(
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

        expected = u'<option value="">---------</option>' \
                   '<option value="00:00:00:00:00:01">' \
                   '00:00:00:00:00:01 ( - 04b4:2104)</option>' \
                   '<option value="00:00:00:00:00:02">' \
                   '00:00:00:00:00:02 ( - 04b4:2104)</option>'
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
            username='nginx',
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
        url = reverse('device.views.server_status', kwargs={'pk': server.pk})
        response = c.get(url, follow=True)
        self.assertRedirects(response,
            'http://testserver/tv/administracao/device/server/', 302)
        urlnotfound = reverse('device.views.server_status', kwargs={'pk': 2})
        response = c.get(urlnotfound, follow=True)
        self.assertEqual(response.status_code, 404, 'Deveria ser 404')

    def test_fileinput_scanfolder(self):
        import re
        server = Server.objects.get(pk=1)
        # Check if the videos folder is acessible
        try:
            server.execute('ls %s' % settings.VLC_VIDEOFILES_DIR)
        except Server.ExecutionFailure:
            raise self.failureException(
                "The %s folder doesn't exists or is inacessible" %
                    settings.VLC_VIDEOFILES_DIR)
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
    u"""
    Test record stream on remote server
    """

    def setUp(self):
        from datetime import datetime, timedelta
        start_time = datetime.now() + timedelta(0, -(3600 * 3))
        self.server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa',
        )
        self.server1 = Server.objects.create(
            name='local1',
            host='127.0.0.2',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa',
        )
        nic_eth0 = NIC.objects.create(
            server=self.server,
            name='eth0',
            ipv4='192.168.0.10',
        )
        NIC.objects.create(
            server=self.server,
            name='eth1',
            ipv4='10.0.1.10',
        )
        nic_lo = NIC.objects.create(
            server=self.server1,
            name='lo:1',
            ipv4='127.0.0.3',
        )
        nic_p1p1 = NIC.objects.create(
            server=self.server1,
            name='p1p1',
            ipv4='10.0.1.11',
        )
        ext_ip = UniqueIP.objects.create(
            port=20000,
            ip='239.10.11.12',
        )
        file = FileInput.objects.create(
            server=self.server,
            filename='/tmp/lala.mpg',
            repeat=True,
            nic_src=nic_eth0
        )
        moutput = MulticastOutput.objects.create(
            server=self.server,
            ip='239.100.100.3',
            port=10000,
            protocol='udp',
            interface=nic_lo,
            sink=ext_ip,
            nic_sink=nic_lo
        )
        moutput1 = MulticastOutput.objects.create(
            server=self.server,
            ip='239.100.100.4',
            port=10000,
            protocol='udp',
            interface=nic_lo,
            sink=ext_ip,
            nic_sink=nic_lo
        )
        ch1 = Channel.objects.create(
            number=10,
            name='Teste 1',
            description='Teste 1',
            channelid='TTT',
            source=moutput
        )
        ch2 = Channel.objects.create(
            number=12,
            name='Teste 2',
            description='Teste 2',
            channelid='TTT',
            source=moutput1
        )
        storage1 = Storage.objects.create(
            folder='/tmp/recording_1',
            server=self.server,
            )
        storage2 = Storage.objects.create(
            folder='/tmp/recording_2',
            server=self.server1,
            )
        StreamRecorder.objects.create(
            server=self.server,
            rotate=60,  # minutos
            storage=storage1,
            keep_time=24,  # horas
            sink=ext_ip,
            nic_sink=nic_eth0,
            channel=ch1,
            start_time=start_time
        )
        StreamRecorder.objects.create(
            server=self.server1,
            rotate=5,  # minutos
            storage=storage2,
            keep_time=2,  # horas
            sink=ext_ip,
            nic_sink=nic_p1p1,
            channel=ch1,
            start_time=start_time
        )
        StreamRecorder.objects.create(
            server=self.server,
            rotate=60,
            storage=storage1,
            keep_time=48,
            sink=ext_ip,
            nic_sink=self.server.nic_set.get(name='eth0'),
            channel=ch2,
            start_time=start_time
        )

    def test_record(self):
        from django.utils import timezone
        from datetime import datetime, timedelta
        start_time = timezone.datetime.utcnow() + timedelta(0, -(3600 * 3))
        srv = self.server
        ext_ip = UniqueIP.objects.create(
            port=20000,
            ip='127.0.0.1',
        )
        storage = Storage.objects.create(
            folder='/tmp/recording_t',
            server=srv,
            )
        recorder = StreamRecorder.objects.create(
            server=srv,
            rotate=60,
            storage=storage,
            keep_time=130,
            sink=ext_ip,
            nic_sink=srv.nic_set.get(name='eth1'),
            channel=Channel.objects.all()[0],
            start_time=start_time
        )
        cmd_expected = u'%s -l %s/%d/  \
-r %d -U -u @127.0.0.1:20000/ifaddr=10.0.1.10 %s/%d' % (
            settings.MULTICAT_COMMAND,
            settings.CHANNEL_RECORD_DISKCONTROL_DIR,
            storage.id,
            (60 * 60 * 27000000),
            recorder.storage.folder,
            recorder.pk,
            )
        self.assertEqual(recorder._get_cmd(), cmd_expected)
        self.assertEqual(cmd_expected, recorder._get_cmd())

    def test_view_tvod_list(self):
        from datetime import datetime, timedelta
        import simplejson as json
        start_time = datetime.now() + timedelta(0, -3600)
        ## Muda o status para rodando
        StreamRecorder.objects.filter(keep_time__gt=80).update(status=True,
            start_time=start_time)
        self.c = Client()
        response = self.c.get(reverse('device.views.tvod_list'))
        self.assertEqual(response.status_code, 200, 'Deveria haver a listagem')
        # Objeto JSON
        decoder = json.JSONDecoder()
        jrecorder = decoder.decode(response.content)
        self.assertEqual(len(jrecorder), 2, 'Deveria haver 2 canais rodando')

    def test_tvod_view(self):
        #from models import StreamPlayer
        urlplay = reverse('device.views.tvod',
            kwargs={'channel_number': 12, 'command': 'play', 'seek': 3600})
        self.assertEqual('/tv/device/tvod/12/play/3600', urlplay,
            'URL invalida')
        urlstopOK = reverse('device.views.tvod',
            kwargs={'channel_number': 12, 'command': 'stop', 'seek': 0})
        self.assertEqual('/tv/device/tvod/12/stop/0', urlstopOK,
            'URL invalida')
        self.c = Client()
        response = self.c.get(urlplay)
        ## TODO: Fazer autenticação
        self.assertContains(response, 'Unauthorized', status_code=401)
        response = self.c.get(urlstopOK)
        self.assertContains(response, 'Unauthorized', status_code=401)

    def test_install_cron(self):
        recorders = StreamRecorder.objects.all()
        cron_1 = '*/30 * * * * /iptv/bin/multicat_expire.sh \
/tmp/recording_1/6/ 25'
        self.assertEqual(cron_1, recorders[0].get_cron_line())
        cron_2 = '*/30 * * * * /iptv/bin/multicat_expire.sh \
/tmp/recording_2/7/ 25'
        self.assertEqual(cron_2, recorders[1].get_cron_line())
        cron_3 = '*/30 * * * * /iptv/bin/multicat_expire.sh \
/tmp/recording_1/8/ 49'
        self.assertEqual(cron_3, recorders[2].get_cron_line())
        recorders[0].install_cron()

    def test_change_recorder_nic(self):
        rec = StreamRecorder.objects.all()[0]
        new_nic = NIC.objects.get(name='eth1')
        rec.nic_sink = new_nic
        rec.save()
        rec1 = StreamRecorder.objects.all()[0]
        self.assertEqual(new_nic, rec1.nic_sink)


class ServerRouteTest(TestCase):
    
    def setUp(self):
        ## create server
        self.server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa',
        )
        nic = NIC.objects.get(ipv4='127.0.0.1')
        ## create multicast input
        MulticastInput.objects.create(
            server=self.server,
            interface=nic,
            port=10000,
            protocol='udp',
            ip='239.0.1.11',
        )

    def test_multicast_input(self):
        multicastin = MulticastInput.objects.get(port=10000)
        expected_cmd = unicode(
            "%s "
            "-D @239.0.1.11:10000/udp "
            "-c %s%d.conf "
            "-r %s%d.sock"
        ) % (settings.DVBLAST_COMMAND,
             settings.DVBLAST_CONFS_DIR, multicastin.pk,
             settings.DVBLAST_SOCKETS_DIR, multicastin.pk,
             )
        self.assertEqual(expected_cmd, multicastin._get_cmd())

        multicastin.start()
        self.assertTrue(multicastin.running())
        self.assertTrue(multicastin.status)
        routes = self.server.list_routes()
        self.assertTrue( ('239.0.1.11', 'lo') in routes )

        multicastin.stop()
        self.assertFalse(multicastin.running())
        self.assertFalse(multicastin.status)
        routes = self.server.list_routes()
        self.assertFalse( ('239.0.1.11', 'lo') in routes )

