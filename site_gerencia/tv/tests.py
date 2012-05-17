#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.test import TestCase, Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from tv.models import Channel
from device.models import *

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
        )
        nic = NIC.objects.get(server=server, ipv4='127.0.0.1')
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
            ip_out='239.0.1.3',
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
            output=ipout,
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

    def test_channel(self):
        self.channel.start()
        self.assertTrue(self.channel._is_streaming())
        self.assertTrue(self.channel._is_recording())
        
        self.channel.stop()
        self.assertFalse(self.channel._is_streaming())
        self.assertFalse(self.channel._is_recording())

