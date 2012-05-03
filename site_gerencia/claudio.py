# -*- encoding:utf-8 -*-

import sys
import os

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(PROJECT_ROOT_PATH)

if PROJECT_ROOT_PATH not in sys.path:
    sys.path.append(PROJECT_ROOT_PATH)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Helber Maciel Guerra', 'helber@cianet.ind.br'),
    ('Gabriel Reitz Giannattasio', 'gartz@cianet.ind.br'),
    ('Eduardo Vieira', 'eduardo@cianet.ind.br'),
    ('Claudio Guirunas', 'claudio@cianet.ind.br'),
)

MANAGERS = ADMINS

if 'test' in sys.argv:
    print('CLAUDIO: TESTE SQLITE')
    ## Banco de dados teste
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
else:
    print('CLAUDIO: DATABASE MYSQL')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'iptv',
            'USER': 'iptv',
            'PASSWORD': 'iptv',
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


#IMPORTANTE:
print('VERIFIQUE LINKS SIMBOLICOS')
# ARRUMAR LINKS SIMBOLICOS DA SEGUINTE FORMA PARA QUE O SISTEMA FUNCIONE CERTO:
# EM /var/www/html
#0 lrwxrwxrwx. 1 nginx nginx   14 Mar  7 10:41 media -> tvfiles/media/
#0 lrwxrwxrwx. 1 nginx nginx   15 Mar  7 10:41 static -> tvfiles/static/
#0 lrwxrwxrwx. 1 nginx nginx    7 Mar  7 10:29 tv -> tvfiles
#4 drwxr-xr-x. 4 nginx nginx 4096 Jan 13 12:23 tvfiles
#
# EM /home/claudio/Projects/iptv-middleware/site_gerencia:
#
#0 lrwxrwxrwx.  1 claudio claudio     22 Mar  7 10:47 tvfiles -> /var/www/html/tvfiles/
#0 lrwxrwxrwx.  1 claudio claudio     27 Mar  7 10:38 media -> /var/www/html/tvfiles/media

MEDIA_URL = '/tv/media/'
MEDIA_ROOT = '/var/www/html/tv/media/'
ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
STATIC_ROOT = '/var/www/html/tv/static/'
STATIC_URL = '/tv/static/'
ROOT_URL = 'tv/'



#ROOT_URL = 'tv/'
#MEDIA_URL = '/tv/media/'
#MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'media')
#ADMIN_MEDIA_PREFIX = '/tv/static/admin/'
#STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'tvfiles', 'static')
#STATIC_URL = '/tv/static/'


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
    'canal',
    # Interface dos setup-box
    'box',
    # Pagina de home
    #'home',
    # Aplicação de controle de stream
    'stream',
    'device',
    # EPG
    'epg',
)

LOGIN_URL = '/%saccounts/login' % ROOT_URL

LOGIN_REDIRECT_URL = '/%sadministracao/' % ROOT_URL

#^/canal/(add|remove|edit|delete)/(.*)$
LOGIN_REQUIRED_URLS = (
    r'^/%scanal/((?!canallist$))$',
    r'^/%sadmin/(.*)$',
)

MULTICAST_DAEMON = '/usr/bin/multicat_daemon'
MULTICAST_COMMAND = '/usr/bin/multicat'
MULTICAST_APP = 'multicat'

DVBLAST_DAEMON = '/usr/bin/dvblast_daemon'
DVBLAST_COMMAND = '/usr/bin/dvblast'
#DVBLAST_COMMAND = '/usr/local/bin/fake_dvblast'
DVBLAST_APP = 'dvblast'
DVBLAST_CONF_DIR = '/etc/dvblast'

CHANNEL_RECORD_DIR = '/mnt/backup/gravacoes'

if DEBUG == True:
    try:
        # Debug-Toolbar https://github.com/robhudson/django-debug-toolbar/
        import debug_toolbar
        INTERNAL_IPS = ('127.0.0.3',)
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

FORCE_SCRIPT_NAME = ""
