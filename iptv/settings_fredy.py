# -*- encoding:utf-8 -*-
import sys
from settings import *
from dev_settings import *
import djcelery
djcelery.setup_loader()

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'iptv',
        'USER': 'iptv',
        'PASSWORD': 'iptv',
        'HOST': '127.0.0.1',
        #'PORT': ,
    }
}

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

TASTYPIE_FULL_DEBUG = True

TASTYPIE_ABSTRACT_APIKEY = False

EPG_IMPORT_CREDENTIALS = {
    'site': 'guide.kingrus.net',
    'username': 'epg',
    'password': 'bhhD.ahg3f',
}

IPTV_LOG_DIR = '%s/log' % PROJECT_ROOT_PATH

if DEBUG is True:
    # Envia todas as mensagens de log para o console
    # http://docs.python.org/dev/library/logging.html#logging.LogRecord
    # http://docs.python.org/2/library/logging.html#logrecord-attributes
    LOGGING['formatters']['verbose']['format'] = '[\033[0;31m%(name)s\033[0m \
%(levelname)s %(relativeCreated)d]\t \033[0;35m%(message)s\033[0m [%(funcName)s(\033[0;34m\
%(pathname)s:%(lineno)d\033[0m)]'
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
        DEBUG_TOOLBAR_PATCH_SETTINGS = False
        DEBUG_TOOLBAR_PANELS = [
            'debug_toolbar.panels.versions.VersionsPanel',
            'debug_toolbar.panels.timer.TimerPanel',
            'debug_toolbar.panels.settings.SettingsPanel',
            'debug_toolbar.panels.headers.HeadersPanel',
            'debug_toolbar.panels.request.RequestPanel',
            'debug_toolbar.panels.sql.SQLPanel',
            'debug_toolbar.panels.staticfiles.StaticFilesPanel',
            'debug_toolbar.panels.templates.TemplatesPanel',
            'debug_toolbar.panels.cache.CachePanel',
            'debug_toolbar.panels.signals.SignalsPanel',
            'debug_toolbar.panels.logging.LoggingPanel',
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ]
        INSTALLED_APPS += ('debug_toolbar',)
        INTERNAL_IPS = ('127.0.0.1',)
        MIDDLEWARE_CLASSES += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )
    except ImportError:
        pass


DVBLAST_DUMMY = './device/helper/dvblast_dummy.py'
DVBLASTCTL_DUMMY = './device/helper/dvblastctl_dummy.py'
MULTICAT_DUMMY = './device/helper/multicat_dummy.py'
MULTICATCTL_DUMMY = './device/helper/multicatctl_dummy.py'
VLC_DUMMY = './device/helper/vlc_dummy.py'

EMAIL_HOST = '127.0.0.1'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 1025
EMAIL_USE_TLS = False