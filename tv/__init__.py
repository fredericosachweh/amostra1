# -*- encoding:utf8 -*

from __future__ import unicode_literals
import django

default_app_config = 'tv.apps.TVConfig'

# Django 1.6.x compat
if django.get_version().startswith('1.6.'):
    from . import dispatch

