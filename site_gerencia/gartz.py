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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if DEBUG == True:
    try:
        # Debug-Toolbar https://github.com/robhudson/django-debug-toolbar/
        import debug_toolbar
        INTERNAL_IPS = ('127.0.0.1',)
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
        MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    except ImportError:
        pass

TASTYPIE_FULL_DEBUG = DEBUG

