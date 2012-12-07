# -*- encoding:utf-8 -*-
from settings import *

import sys
import os

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(PROJECT_ROOT_PATH)


DEBUG = True

#if 'test' in sys.argv:
#    ## Banco de dados teste
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.sqlite3',
#            'NAME': os.path.join(PROJECT_ROOT_PATH, 'sqlite.db'),
#            'USER': '',
#            'PASSWORD': '',
#            'HOST': '',
#            'PORT': ''
#        }
#    }
#elif 'dev' in sys.argv:
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'iptv',
            'USER': 'cioban',
            'PASSWORD': 'sergio',
            'HOST': '10.5.5.254',
            'PORT': '3306'
        }
    }
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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',
    # South http://south.aeracode.org/docs/
    #'south',
    # Interface dos setup-box
    'box',
    # Aplicação de controle de stream
    'device',
    # EPG
    'epg',
    # App with info about possible frequencies to tune
    'dvbinfo',
    # TV
    'tv',
    # Tools app
    'tools',
    'monitoramento',
)

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

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'lib.middleware.login.RequireLoginMiddleware',
)


# Auxiliar apps configuration
MULTICAT_COMMAND = '/iptv/bin/multicat'
MULTICAT_LOGS_DIR = '/iptv/var/log/multicat/'
MULTICAT_SOCKETS_DIR = '/iptv/var/run/multicat/sockets/'

CHANNEL_RECORD_DIR = '/var/lib/iptv/recorder'
CHANNEL_RECORD_CLEAN_COMMAND = '/iptv/bin/multicat_expire.sh'
CHANNEL_PLAY_PORT = 12000

DVBLAST_COMMAND = '/iptv/bin/dvblast'
DVBLAST_CONFS_DIR = '/iptv/etc/dvblast/'
DVBLAST_LOGS_DIR = '/iptv/var/log/dvblast/'
DVBLAST_SOCKETS_DIR = '/iptv/var/run/dvblast/sockets/'

DVBLASTCTL_COMMAND = '/iptv/bin/dvblastctl'


# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lx2'

if DEBUG is True:
    # Envia todas as mensagens de log para o console
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
    try:
        import django_extensions
        INSTALLED_APPS += ('django_extensions',)
    except ImportError:
        pass
    try:
        # Debug-Toolbar https://github.com/robhudson/django-debug-toolbar/
        import debug_toolbar
        DEBUG_TOOLBAR_PANELS = (
            'debug_toolbar.panels.version.VersionDebugPanel',
            'debug_toolbar.panels.timer.TimerDebugPanel',
            'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
            'debug_toolbar.panels.headers.HeaderDebugPanel',
            'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
            'debug_toolbar.panels.template.TemplateDebugPanel',
            'debug_toolbar.panels.sql.SQLDebugPanel',
            'debug_toolbar.panels.signals.SignalDebugPanel',
            'debug_toolbar.panels.logger.LoggingPanel',
        )
        INSTALLED_APPS += ('debug_toolbar',)
        INTERNAL_IPS = ('127.0.0.1',)
        MIDDLEWARE_CLASSES += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )
    except ImportError:
        pass
