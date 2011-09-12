#!/usr/bin/env python
import os
import sys

path = os.path.dirname(__file__)+'/site_gerencia'
if path not in sys.path:
    sys.path.append(path)

#print(sys.path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
