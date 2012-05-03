# -*- encoding:utf-8 -*-

import sys
import os

from settings import *

DEBUG = True

if 'test' in sys.argv:
    print('CLAUDIO: TESTE SQLITE')
    ## Banco de dados teste
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
else:
    print('CLAUDIO: DATABASE MYSQL')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'iptv',
            'USER': 'iptv',
            'PASSWORD': 'iptv',
            'HOST': '127.0.0.1',
            'PORT': '3306'
        }

    }

MEDIA_URL = '/tv/media/'
MEDIA_ROOT = '/var/www/html/tv/media/'
ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
STATIC_ROOT = '/var/www/html/tv/static/'
STATIC_URL = '/tv/static/'
ROOT_URL = 'tv/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lx3'

