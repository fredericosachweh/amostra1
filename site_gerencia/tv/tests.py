#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from tv.models import Channel
from django.test import TestCase
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from device.models import Server, NIC, UnicastInput, DemuxedService
from device.models import UniqueIP, MulticastOutput, StreamRecorder
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.conf import settings


@override_settings(DVBLAST_COMMAND=settings.DVBLAST_DUMMY)
@override_settings(DVBLASTCTL_COMMAND=settings.DVBLASTCTL_DUMMY)
@override_settings(MULTICAT_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(MULTICATCTL_COMMAND=settings.MULTICATCTL_DUMMY)
@override_settings(VLC_COMMAND=settings.VLC_DUMMY)
class ChannelTest(TestCase):
    """
    Testes dos canais de televisão
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
        nic = NIC.objects.create(server=server, ipv4='127.0.0.1')
        unicastin = UnicastInput.objects.create(
            server=server,
            interface=nic,
            port=30000,
            protocol='udp',
        )
        service = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )
        internal = UniqueIP.create(sink=service)
        ipout = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        self.channel = Channel.objects.create(
            number=51,
            name='Discovery Channel',
            description='Cool tv channel',
            channelid='DIS',
            image='',
            enabled=True,
            source=ipout,
        )
        recorder = StreamRecorder.objects.create(
            server=server,
            rotate=60,
            sink=internal,
            nic_sink=nic,
            keep_time=168,
            channel=self.channel,
        )

    def tearDown(self):
        Server.objects.all().delete()


class APITest(TestCase):
    """
    Test API for ERP
    """

    def setUp(self):
        import getpass
        super(APITest, self).setUp()
        server = Server.objects.create(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username=getpass.getuser(),
            rsakey='~/.ssh/id_rsa',
            offline_mode=True,
        )
        nic = NIC.objects.create(server=server, ipv4='127.0.0.1')
        unicastin = UnicastInput.objects.create(
            server=server,
            interface=nic,
            port=30000,
            protocol='udp',
        )
        service = DemuxedService.objects.create(
            server=server,
            sid=1,
            sink=unicastin,
            nic_src=nic,
        )
        internal = UniqueIP.create(sink=service)
        ipout1 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.2',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        ipout2 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.3',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        ipout3 = MulticastOutput.objects.create(
            server=server,
            ip='239.0.1.4',
            interface=nic,
            sink=internal,
            nic_sink=nic,
        )
        self.channel1 = Channel.objects.create(
            number=51,
            name='Discovery Channel',
            description='Cool tv channel',
            channelid='DIS',
            image='',
            enabled=True,
            source=ipout1,
        )
        self.channel2 = Channel.objects.create(
            number=13,
            name='Globo',
            description=u'Rede globo de televisão',
            channelid='GLB',
            image='',
            enabled=True,
            source=ipout2,
            )
        self.channel3 = Channel.objects.create(
            number=14,
            name='Test 3',
            description=u'Rede Test 3',
            channelid='GLB',
            image='',
            enabled=True,
            source=ipout3,
            )

    def tearDown(self):
        Server.objects.all().delete()

    def test_created(self):
        channels = Channel.objects.all()
        self.assertEqual(3, channels.count())

    def test_call_schema(self):
        c = Client()
        #api_dispatch_list,api_get_schema,api_get_multiple,api_dispatch_detail
        #e = resolve('/tv/api/epg/v1/channel/')
        #print('epg=%s' % e)
        #t = resolve('/tv/api/tv/v1/channel/')
        #print('tv=%s' % t)
        urlschema = reverse('tv:api_get_schema',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual(urlschema, '/tv/api/tv/v1/channel/schema/')
        response = c.get(urlschema)
        self.assertContains(response, 'channelid', 1, 200)

    def test_list_channels(self):
        c = Client()
        url = reverse('tv:api_dispatch_list',
            kwargs={'resource_name': 'channel', 'api_name': 'v1'})
        self.assertEqual(url, '/tv/api/tv/v1/channel/')
        response = c.get(url)
        import simplejson as json
        # Objeto JSON
        decoder = json.JSONDecoder()
        jcanal = decoder.decode(response.content)
        self.failUnlessEqual(jcanal['meta']['total_count'], 3,
            'Deveria haver 3 canais')

    def test_channel2(self):
        c = Client()
        url = reverse('tv:api_dispatch_detail',
            kwargs={'pk': '2', 'api_name': 'v1', 'resource_name': 'channel'})
        self.assertEqual(url, '/tv/api/tv/v1/channel/2/')
        response = c.get(url)
        import simplejson as json
        # Objeto JSON
        decoder = json.JSONDecoder()
        jcanal = decoder.decode(response.content)
        self.failUnlessEqual(jcanal['description'], u'Rede globo de televisão')
        self.failUnlessEqual(jcanal['name'], u'Globo')


class WizardTest(LiveServerTestCase):
    fixtures = ['user-data.json', 'default-server.json',
                'antenna.json', 'dvbworld.json', 'pixelview.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(WizardTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(WizardTest, cls).tearDownClass()
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

    def test_wizard(self):
        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:channel_wizard_add'))
        self.selenium.get(add_new_url)
        # wizard's first step
        self._select('id_0-input_types_field', 'Arquivo de entrada')
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_xpath(
                "//option[@value='1']"))
        self._select('id_0-input_stream', 'asdf [dvb] asdf -->')
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_element_by_tag_name('body'))
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
#        name = self.selenium.find_element_by_name('0-name')
#        ip = self.selenium.find_element_by_name('0-ip')
#        port = self.selenium.find_element_by_name('0-port')
#        name.send_keys('programa1')
#        ip.send_keys('192.168.0.135')
#        port.send_keys('1000')
        # 2nd step
        sid = self.selenium.find_element_by_name('1-sid')
        sid.send_keys('123')
        object_id = self.selenium.find_element_by_name('1-object_id')
        object_id.send_keys('123')
        self._select('id_1-content_type', 'Entrada IP multicast')
        print self.selenium.find_element_by_class_name(
                                        'form-row field-content_type')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
        # 3rd step
        self._select('id_2-content_type', 'Endereço IPv4 multicast')
        self._select('id_2-nic_sink', 'localhost')
        object_id = self.selenium.find_element_by_name('1-object_id')
        rotate = self.selenium.find_element_by_name('id_2-rotate')
        keep_time = self.selenium.find_element_by_name('id_2-keep_time')
        start_time = self.selenium.find_element_by_name('id_2-start_time')
        object_id.send_keys('123')
        rotate.send_keys('321')
        keep_time.send_keys('213')
        start_time.send_keys('21/05/2012')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
        # 4th step
        self._select('id_3-content_typ', 'Endereço IPv4 multicast')
        self._select('id_3-protocol', 'UDP')
        self._select_by_value('id_3-interface', 1)
        self._select_by_value('id_3-nic_sink', 1)
        object_id = self.selenium.find_element_by_name('id_3-object_id')
        port = self.selenium.find_element_by_name('id_3-port')
        ip = self.selenium.find_element_by_name('id_3-ip')
        object_id.send_keys('123')
        port.send_keys('1000')
        ip.send_keys('192.168.0.1')
        # 5th step
        self._select('id_4-source', 1)
        number = self.selenium.find_element_by_name('id_4-numero')
        name = self.selenium.find_element_by_name('id_4-nome')
        #logo?
        acronym = self.selenium.find_element_by_name('4-sigla')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
