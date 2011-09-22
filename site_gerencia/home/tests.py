#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
Testes unitários do aplicativo home
"""

from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.core.urlresolvers import reverse

class TestRegression(TestCase):
    """Testes de Regressão"""

    def test_regress_home(self):
        """A página home precisa existir."""
        c = Client()
        url = reverse('home.views.home')
        home = c.get(url,{})
        self.assertEquals(home.status_code,200,'Página home não existe')

