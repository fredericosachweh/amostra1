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
            'USER': 'iptv',
            'PASSWORD': 'b9099d8d71e30342ce95ecf3597c5d79',
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


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'lib.middleware.login.RequireLoginMiddleware',
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lx2'

if DEBUG is True:
    ## Envia todas as mensagens de log para o console
    #for logger in LOGGING['loggers']:
    #    LOGGING['loggers'][logger]['handlers'] = ['console']
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
        MIDDLEWARE_CLASSES += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )
    except ImportError:
        pass



INTERNAL_IPS = ('127.0.0.1',)
