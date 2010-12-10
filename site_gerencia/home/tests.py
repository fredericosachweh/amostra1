#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
Testes unitários do aplicativo home
"""

from django.test import TestCase
from django.test import Client

class TestRegression(TestCase):
    """Testes de Regressão"""

    def test_regress_home(self):
        """A página home precisa existir."""
        c = Client()
        home = c.get('/',{})
        self.assertEquals(home.status_code,200,'Página home não existe')

