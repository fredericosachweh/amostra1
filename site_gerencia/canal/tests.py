#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários wizard
"""

import os
from django.test import TestCase
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from django.test.client import Client
from django.test.client import RequestFactory
from django.conf import settings

from device.models import *

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

@override_settings(DVBLAST_COMMAND=settings.DVBLAST_DUMMY)
@override_settings(DVBLASTCTL_COMMAND=settings.DVBLASTCTL_DUMMY)
@override_settings(MULTICAT_COMMAND=settings.MULTICAT_DUMMY)
@override_settings(MULTICATCTL_COMMAND=settings.MULTICATCTL_DUMMY)
@override_settings(VLC_COMMAND=settings.VLC_DUMMY)


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

    def test_wizard(self):
        self._login('admin', 'cianet')
        add_new_url = '%s%s' % (self.live_server_url,
                                reverse('admin:canal_wizard_add'))
        self.selenium.get(add_new_url)
        # wizard's first step
        self._select_by_value('id_0-server', 1)
        name = self.selenium.find_element_by_name('0-name')
        ip = self.selenium.find_element_by_name('0-ip')
        port = self.selenium.find_element_by_name('0-port')        
        name.send_keys('programa1')
        ip.send_keys('192.168.0.135')
        port.send_keys('1000')
        self.selenium.find_element_by_xpath('//input[@name="_save"]').click()
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

