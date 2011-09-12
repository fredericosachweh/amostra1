# -*- encoding:utf-8 -*-

import sys,os

PROJECT_ROOT_PATH = os.path.dirname(__file__)
if PROJECT_ROOT_PATH not in sys.path:
    sys.path.append(PROJECT_ROOT_PATH)

ROOT_DIR = PROJECT_ROOT_PATH

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Helber Maciel Guerra', 'helber@cianet.ind.br'),
)

MANAGERS = ADMINS

if 'test' in sys.argv:
    ## Banco de dados teste
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ROOT_DIR+'/sqlite.db',
            'USER':'',
            'PASSWORD':'',
            'HOST':'',
            'PORT':''
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'multicat',                      # Or path to database file if using sqlite3.
            'USER': 'multicat',                      # Not used with sqlite3.
            'PASSWORD': 'multicat',                  # Not used with sqlite3.
            'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
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

if 'runserver' in sys.argv:
    MEDIA_URL = 'http://127.0.0.1:8000/media/'
    MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH,'media/')
    #ADMIN_MEDIA_PREFIX = '/static_admin/admin/'
    ADMIN_MEDIA_PREFIX = '/static/'
    STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH,'static/')
    STATIC_URL = '/static/'
    ROOT_URL = '/'
else:
    MEDIA_URL = '/multicat/static/'
    MEDIA_ROOT = '/mnt/projetos/ativos/cianet/site-multicat/site_multicat/static/'
    ADMIN_MEDIA_PREFIX = '/multicat/static/admin/'
    STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH,'static/')
    STATIC_URL = '/static/'
    ROOT_URL = '/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lxl'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lib.middleware.login.RequireLoginMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT_PATH,'templates/')
)

#FIXTURE_DIRS = '/mnt/projetos/ativos/cianet/site_gerencia/site_gerencia/canal/fixtures/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    # Testes com nose
    #'django_nose',
    # Gestao de canal
    'canal',
    # Interface dos setup-box
    'box',
    # Pagina de home
    'home',
    # Aplicação de controle de stream
    'stream',
)

#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

#USE_TERMINAL_COLORS=True

LOGIN_URL = ROOT_URL+'accounts/login'

LOGIN_REDIRECT_URL = ROOT_URL+'administracao/'

#^/canal/(add|remove|edit|delete)/(.*)$
LOGIN_REQUIRED_URLS = (
    r'^/canal/((?!canallist$))$',
    r'^/admin/(.*)$',
)

#MULTICAST_APP = '/usr/local/bin/multicat'
MULTICAST_COMMAND = '/usr/local/bin/roda'
MULTICAST_APP = 'multicat'

