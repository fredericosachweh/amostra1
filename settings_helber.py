# -*- encoding:utf-8 -*-
from settings import *

#from dbsettings.utils import set_defaults

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
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'iptv',
            'USER': 'iptv',
            'PASSWORD': 'iptv',
            'HOST': '127.0.0.1',
            'PORT': 5432,
        },
        'test_iptv': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'test_iptv',
            'USER': 'test_iptv',
            'PASSWORD': 'test_iptv',
            'HOST': '127.0.0.1',
            'PORT': 5432,
        },
        'mylocal': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'iptv',
            'USER': 'iptv',
            'PASSWORD': 'iptv',
            'HOST': '/var/lib/mysql/mysql.sock',
            'PORT': '',
        },
        'pg92': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'iptv',
            'USER': 'iptv',
            'PASSWORD': 'iptv',
            'HOST': '127.0.0.1',
            'PORT': '5433',
        },
        'my49': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'iptv',
            'USER': 'helber',
            'PASSWORD': 'helber',
            'HOST': '10.1.1.49',
            'PORT': '3306',
        }
    }
    #DATABASES['default'] = DATABASES['pglocal']
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'iptv',
#        'USER': 'iptv',
#        'PASSWORD': 'iptv',
#        'HOST': '127.0.0.1',
#        'PORT': 5432,
#    }
#}

ROOT_URL = 'tv/'
MEDIA_URL = '/tv/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'media')
ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'static')
STATIC_URL = '/tv/static/'
#ROOT_URLCONF = '/tv'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lx2'

TASTYPIE_FULL_DEBUG = False
##Black       0;30     Dark Gray     1;30
##Blue        0;34     Light Blue    1;34
##Green       0;32     Light Green   1;32
##Cyan        0;36     Light Cyan    1;36
##Red         0;31     Light Red     1;31
##Purple      0;35     Light Purple  1;35
##Brown       0;33     Yellow        1;33
##Light Gray  0;37     White         1;37

#GREEN="\033[0;32m";
#BLUE="\033[0;34m";
#RED="\033[0;31m";
#GRAY="\033[0;30m";
#PURPLE="\033[0;35m";
#LPURPLE="\033[1;35m";
#NO_COLOUR="\033[0m";

if DEBUG is True:
    # Envia todas as mensagens de log para o console
    # http://docs.python.org/dev/library/logging.html#logging.LogRecord
    LOGGING['formatters']['verbose']['format'] = '[\033[0;31m%(name)s\033[0m \
%(levelname)s %(relativeCreated)d]\t %(message)s [%(funcName)s(\033[0;34m\
%(filename)s:%(lineno)d\033[0m)]'
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

EPG_IMPORT_CREDENTIALS = {
    'site': '83.222.124.34',
    'username': '91037581920@revistaeletronica.com.br',
    'password': '91037581920',
}
