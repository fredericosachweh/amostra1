# -*- encoding:utf8 -*

from __future__ import unicode_literals
from django.conf import settings
import os

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')

# Create the dir if it still doesn't exist
try:
    os.makedirs(os.path.join(MEDIA_ROOT, 'epg'))
except:
    pass


default_app_config = 'epg.apps.EPGConfig'
