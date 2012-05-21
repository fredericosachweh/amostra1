# -*- encoding:utf-8 -*-

import sys
import os

from settings import *

DEBUG = True

if 'test' in sys.argv:
    ## Banco de dados teste
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_ROOT_PATH, 'sqlite.db'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': ''
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'iptv',
            'USER': 'root',
            'PASSWORD': 'cianet',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }

ROOT_URL = 'tv/'
MEDIA_URL = '/tvfiles/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'media')
ADMIN_MEDIA_PREFIX = '/tvfiles/static/admin/'
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'static')
STATIC_URL = '/tvfiles/static/'
#ROOT_URLCONF = '/tv'

INTERNAL_IPS = ('127.0.0.1',)

#MessageMiddleware
#from django.contrib.messages.middleware.MessageMiddleware
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'lib.middleware.login.RequireLoginMiddleware',
)
