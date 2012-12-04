# -*- encoding:utf-8 -*-
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
            #'ENGINE': 'django.db.backends.mysql',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'iptv',
            'USER': 'iptv',
            'PASSWORD': 'iptv',
            #'HOST': '/var/lib/mysql/mysql.sock',
            'HOST': '127.0.0.1',
            #'PORT': '',
            'PORT': '5432',
        }
    }

ROOT_URL = 'tv/'
MEDIA_URL = '/tv/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'media')
ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'static')
STATIC_URL = '/tv/static/'
#ROOT_URLCONF = '/tv'


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

TASTYPIE_FULL_DEBUG = True

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

EPG_IMPORT_CREDENTIALS = {
    'site': 'revistaeletronica.com.br',
    'username': '91037581920@revistaeletronica.com.br',
    'password': '91037581920',
}
