# -*- encoding:utf-8 -*-

import sys
import os

from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#DATABASES = {
#	'default': {
#	    'ENGINE': 'django.db.backends.sqlite3',
#	    'NAME': os.path.join(PROJECT_ROOT_PATH,'sqlite.db'),
#	    'USER':'',
#	    'PASSWORD':'',
#	    'HOST':'',
#	    'PORT':''
#	}
#}

DATABASES = {
    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'iptv',
#        'USER': 'iptv',
#        'PASSWORD': 'iptv',
#        'HOST': '127.0.0.1',
#        'PORT': '5432',

        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'iptv',
        'USER': 'cioban',
        'PASSWORD': 'sergio',
        'HOST': '10.1.1.49',
        'PORT': '3306'
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
