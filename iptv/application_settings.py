# -*- encoding:utf8 -*-

import os

from .settings import PROJECT_ROOT_PATH

USE_TZ = True
WSGI_APPLICATION = 'iptv.wsgi.application'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_URL = '/tv/media/'
MEDIA_ROOT = '/iptv/var/www/html/tvfiles/media/'
STATIC_ROOT = '/iptv/var/www/html/tvfiles/static/'
STATIC_URL = '/tv/static/'
ROOT_URL = 'tv/'

# Porta que o servidor web está configurado
MIDDLEWARE_WEBSERVICE_PORT = 8800

LOGIN_URL = '/%saccounts/login' % ROOT_URL
LOGIN_REDIRECT_URL = '/%sadministracao/' % ROOT_URL

LOGIN_REQUIRED_URLS = (
    r'^/%scanal/((?!canallist$))$',
    r'^/%sadmin/(.*)$',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=rz16epry+8okcm#e=n_m4f4by*-q6-rf^hci!)2yjvadk4lxl'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lib.middleware.login.APIKeyLoginMiddleware',
)

ROOT_URLCONF = 'iptv.urls'


TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Nose tests
    # 'django_nose',
    # Aplicação de controle de stream
    'device',
    # EPG
    'epg',
    # App with info about possible frequencies to tune
    'dvbinfo',
    # TV
    'tv',
    # Video on demand
    #'vod',
    # Node bridge
    'nbridge',
    # Tools app
    'tools',
    # Client
    'client',
    # Django tastypie
    'tastypie',
    # AppSettings
    'dbsettings',
    # Aplicativo de monitoramento
    'monitoramento',
)

LOGIN_URL = '/%saccounts/login' % ROOT_URL

LOGIN_REDIRECT_URL = '/%sadministracao/' % ROOT_URL

STB_USER_PREFIX = 'STB_'
