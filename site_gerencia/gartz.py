# -*- encoding:utf-8 -*-

import sys
import os

from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
	'default': {
	    'ENGINE': 'django.db.backends.sqlite3',
	    'NAME': os.path.join(PROJECT_ROOT_PATH,'sqlite.db'),
	    'USER':'',
	    'PASSWORD':'',
	    'HOST':'',
	    'PORT':''
	}
}

ROOT_URL = 'tv/'
MEDIA_URL = '/tvfiles/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH,'tvfiles','media')
ADMIN_MEDIA_PREFIX = '/tvfiles/static/admin/'
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH,'tvfiles','static')
STATIC_URL = '/tvfiles/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lx1'

INTERNAL_IPS = ('127.0.0.1',)

