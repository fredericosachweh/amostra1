# -*- encoding:utf-8 -*-
from settings import *

import sys
import os

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(PROJECT_ROOT_PATH)


DEBUG = True

#if 'test' in sys.argv:
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
#elif 'dev' in sys.argv:
#DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.mysql',
#            'NAME': 'iptv',
#            'USER': 'cioban',
#            'PASSWORD': 'sergio',
#            'HOST': '10.1.1.49',
#            #'HOST': '10.5.5.254',
#            #'HOST': '127.0.0.1',
#            'PORT': '3306'
#        }
#    }
#else:
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.mysql',
#            'NAME': 'iptv',
#            'USER': 'cianet',
#            'PASSWORD': 'cianet',
#            'HOST': '127.0.0.1',
#            'PORT': '3306'
#        }
#    }

ROOT_URL = 'tv/'
MEDIA_URL = '/tv/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'media')
ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'static')
STATIC_URL = '/tv/static/'
#ROOT_URLCONF = '/tv'

IPTV_LOG_DIR = PROJECT_ROOT_PATH + '/log'


## Color: \033[35m \033[0m
# \t%(module)s->%(funcName)s->%(lineno)d
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s %(funcName)s\
(%(filename)s:%(lineno)d)] \t%(message)s'
        },
        'simple': {
            'format': '%(levelname)s\t%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file.debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/debug.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.device.remotecall': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/remote-call.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'debug': {
            'handlers': ['file.debug'],
            'level': 'DEBUG',
            'propagate': True
        },
        'device.view': {
            'handlers': ['file.debug'],
            'level': 'DEBUG',
            'propagate': True
        },
        'device.remotecall': {
            'handlers': ['file.device.remotecall'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

