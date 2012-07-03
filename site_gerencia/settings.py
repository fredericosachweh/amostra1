# -*- encoding:utf-8 -*-

import sys
import os

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(PROJECT_ROOT_PATH)

if PROJECT_ROOT_PATH not in sys.path:
    sys.path.append(PROJECT_ROOT_PATH)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Helber Maciel Guerra', 'helber@cianet.ind.br'),
    ('Gabriel Reitz Giannattasio', 'gartz@cianet.ind.br'),
    ('Eduardo Vieira', 'eduardo@cianet.ind.br'),
    ('Claudio Guirunas', 'claudio@cianet.ind.br'),
)

MANAGERS = ADMINS

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
            'PORT': '3306'
        }

    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Novo no django 1.4
USE_TZ = False
#WSGI_APPLICATION = 'wsgi.application'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_URL = '/tv/media/'
MEDIA_ROOT = '/var/www/html/tv/media/'
ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
STATIC_ROOT = '/var/www/html/tv/static/'
STATIC_URL = '/tv/static/'
ROOT_URL = 'tv/'

# Porta que o servidor web está configurado
MIDDLEWARE_WEBSERVICE_PORT = 80

LOGIN_URL = '/%saccounts/login' % ROOT_URL
LOGIN_REDIRECT_URL = '/%sadministracao/' % ROOT_URL

#^/canal/(add|remove|edit|delete)/(.*)$
LOGIN_REQUIRED_URLS = (
    r'^/%scanal/((?!canallist$))$',
    r'^/%sadmin/(.*)$',
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lxl'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(PROJECT_ROOT_PATH,'tvfiles','static'),
    #'/var/www/html/%sstatic/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
#MessageMiddleware
#from django.contrib.messages.middleware.MessageMiddleware
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'lib.middleware.login.RequireLoginMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT_PATH, 'templates')
)

IPTV_LOG_DIR = '/iptv/var/log'

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
    # Gestao de canal
    #'canal',
    # Interface dos setup-box
    'box',
    # Pagina de home
    #'home',
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
)

LOGIN_URL = '/%saccounts/login' % ROOT_URL

LOGIN_REDIRECT_URL = '/%sadministracao/' % ROOT_URL

#^/canal/(add|remove|edit|delete)/(.*)$
LOGIN_REQUIRED_URLS = (
    r'^/%scanal/((?!canallist$))$',
    r'^/%sadmin/(.*)$',
)


# Auxiliar apps configuration
MULTICAT_COMMAND = '/iptv/bin/multicat'
MULTICAT_LOGS_DIR = '/iptv/var/log/multicat/'
MULTICAT_SOCKETS_DIR = '/iptv/var/run/multicat/sockets/'

CHANNEL_RECORD_DIR = '/var/lib/iptv/recorder'
CHANNEL_RECORD_COMMAND = '/iptv/bin/multicat'
CHANNEL_RECORD_PLAY_COMMAND = '/iptv/bin/multicat'
CHANNEL_RECORD_CLEAN_COMMAND = '/iptv/bin/multicat_expire.sh'
CHANNEL_PLAY_PORT = 12000

DVBLAST_COMMAND = '/iptv/bin/dvblast'
DVBLAST_CONFS_DIR = '/iptv/etc/dvblast/'
DVBLAST_LOGS_DIR = '/iptv/var/log/dvblast/'
DVBLAST_SOCKETS_DIR = '/iptv/var/run/dvblast/sockets/'

DVBLASTCTL_COMMAND = '/iptv/bin/dvblastctl'

VLC_COMMAND = '/usr/bin/cvlc'
VLC_VIDEOFILES_DIR = '/var/lib/iptv/videos/'
VLC_LOGS_DIR = '/iptv/var/log/vlc/'

INTERNAL_IP_MASK = '239.10.%d.%d'
EXTERNAL_IP_MASK = '239.1.%d.%d'

if 'test' in sys.argv:
    from tempfile import mkdtemp
    # Create a temporary dir for when running tests
    tmpdir = mkdtemp(prefix='iptv-test-')
    # Change vars to point the new location
    MULTICAT_LOGS_DIR = tmpdir + MULTICAT_LOGS_DIR
    os.makedirs(MULTICAT_LOGS_DIR)
    MULTICAT_SOCKETS_DIR = tmpdir + MULTICAT_SOCKETS_DIR
    os.makedirs(MULTICAT_SOCKETS_DIR)
    DVBLAST_CONFS_DIR = tmpdir + DVBLAST_CONFS_DIR
    os.makedirs(DVBLAST_CONFS_DIR)
    DVBLAST_LOGS_DIR = tmpdir + DVBLAST_LOGS_DIR
    os.makedirs(DVBLAST_LOGS_DIR)
    DVBLAST_SOCKETS_DIR = tmpdir + DVBLAST_SOCKETS_DIR
    os.makedirs(DVBLAST_SOCKETS_DIR)
    VLC_VIDEOFILES_DIR = tmpdir + VLC_VIDEOFILES_DIR
    os.makedirs(VLC_VIDEOFILES_DIR)
    CHANNEL_RECORD_DIR = tmpdir + CHANNEL_RECORD_DIR
    os.makedirs(CHANNEL_RECORD_DIR)
    # Pseudo executables folder
    HELPER_FOLDER = os.path.join(PROJECT_ROOT_PATH, 'device', 'helper')
    # Settings to replace
    DVBLAST_DUMMY = os.path.join(HELPER_FOLDER, 'dvblast_dummy.py')
    DVBLASTCTL_DUMMY = os.path.join(HELPER_FOLDER, 'dvblastctl_dummy.py')
    MULTICAT_DUMMY = os.path.join(HELPER_FOLDER, 'multicat_dummy.py')
    MULTICATCTL_DUMMY = os.path.join(HELPER_FOLDER, 'multicatctl_dummy.py')
    VLC_DUMMY = os.path.join(HELPER_FOLDER, 'vlc_dummy.py')

TASTYPIE_FULL_DEBUG = DEBUG

FORCE_SCRIPT_NAME = ""
