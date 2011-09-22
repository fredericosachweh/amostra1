#!/usr/bin/env python
# -*- coding:utf8 -*-

from django.test import TestCase
from models import SetupBox, PushServer
from fields import MACAddressFormField

from django.forms import ValidationError

class SetUpBoxTest(TestCase):
    ##@skipIfDBFeature('supports_transactions')
    def testSetupBox(self):
        """Teste do objeto SetupBox."""
        server = PushServer()
        server.address = '127.0.0.1'
        server.hostname = '127.0.0.1'
        server.port = 8000
        server.save()
        b = SetupBox()
        b.pushserver = server
        b.save()
        b.mac = 'invalid mac'
        b.clean()
        b.save()
        self.assertTrue(b.id, 'SetupBox não pode ser salvo')
        self.assertEquals(b.mac,'invalid mac')
    ##@skipIfDBFeature('supports_transactions')
    def testFormSetupBox(self):
        """Teste do campo MAC do SetupBox."""
        form = MACAddressFormField()
        try:
            form.clean('56:86:E6:5A:F5:4G')
            self.assertFalse(True, 'Não deveria chegar aqui')
        except ValidationError:
            pass
        try:
            form.clean('AF:00:66:22:BA:00')
        except ValidationError:
            self.assertFalse(True, 'Erro na validação do campo')


