# -*- encoding:utf-8 -*-

import sys
import os

PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_PATH = os.path.dirname(PROJECT_ROOT_PATH)

if PROJECT_ROOT_PATH not in sys.path:
    sys.path.append(PROJECT_ROOT_PATH)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Helber Maciel Guerra', 'helber@cianet.ind.br'),
    ('Emanoel Monster', 'emanoel@cianet.ind.br'),
    ('Suporte Kingrus', 'suporte-kingrus@cianet.ind.br'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'iptv',
        'USER': 'iptv',
        'PASSWORD': 'iptv',
        'HOST': '/tmp',
        'CONN_MAX_AGE': 120,  # Tempo em segundos (persistente)
        #'PORT': '5432'
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

# Auxiliar apps configuration
MULTICAT_COMMAND = '/iptv/bin/multicat -N'
MULTICAT_LOGS_DIR = '/iptv/var/log/multicat/'
MULTICAT_SOCKETS_DIR = '/iptv/var/run/multicat/sockets/'
MULTICATCTL_COMMAND = '/iptv/bin/multicatctl'

CHANNEL_RECORD_USE_PCRPID = False
CHANNEL_RECORD_DIR = '/var/lib/iptv/recorder'
CHANNEL_RECORD_COMMAND = '/iptv/bin/multicat -N'
CHANNEL_RECORD_PLAY_COMMAND = '/iptv/bin/multicat -N'
CHANNEL_RECORD_CLEAN_COMMAND = '/iptv/bin/multicat_expire.sh'
CHANNEL_PLAY_PORT = 12000
CHANNEL_RECORD_DISKCONTROL = '/iptv/bin/diskctrl'
CHANNEL_RECORD_DISKCONTROL_DIR = '/iptv/var/run/diskctrl'
CHANNEL_RECORD_DISKCONTROL_VERBOSE = True


DVBLAST_COMMAND = '/iptv/bin/dvblast'
DVBLAST_CONFS_DIR = '/iptv/etc/dvblast/'
DVBLAST_LOGS_DIR = '/iptv/var/log/dvblast/'
DVBLAST_SOCKETS_DIR = '/iptv/var/run/dvblast/sockets/'

DVBLASTCTL_COMMAND = '/iptv/bin/dvblastctl'

VLC_COMMAND = '/usr/bin/cvlc'
VLC_VIDEOFILES_DIR = '/var/lib/iptv/videos/'
VLC_LOGS_DIR = '/iptv/var/log/vlc/'

FFMPEG_COMMAND = '/usr/bin/ffmpeg'
FFMPEG_LOGS_DIR = '/iptv/var/log/ffmpeg/'

INTERNAL_IP_MASK = '239.10.%d.%d'
EXTERNAL_IP_MASK = '239.1.%d.%d'

NODEJS_COMMAND = '/usr/bin/node'
NBRIDGE_COMMAND = '/iptv/usr/lib/nbridge/main.js'
NBRIDGE_LOGS_DIR = '/iptv/var/log/nbridge/'
NBRIDGE_SOCKETS_DIR = '/iptv/var/run/nbridge/'
NBRIDGE_UPSTREAM_DIR = '/iptv/etc/nginx-fe/upstream/'
NBRIDGE_UPSTREAM = '/iptv/etc/nginx-fe/upstream/nbridge.conf'
NBRIDGE_CONF_DIR = '/iptv/etc/nbridge/'
NBRIDGE_SERVER_KEY = '36410c96-c157-4b2a-ac19-1a2b7365ca11'

from .dev_settings import *

from .log_settings import LOGGING

from .application_settings import *

RPM_CHECK_VERSION = """\
site_iptv \
multicat \
dvblast \
frontend_iptv \
nodejs-nbridge \
nginx-fe \
nginx-mw \
"""

EPG_IMPORT_CREDENTIALS = {
    'site': 'guide.kingrus.net',
    'username': 'epg',
    'password': 'bhhD.ahg3f',
}

ALLOWED_HOSTS = [
    '.middleware.iptvdomain', '*'
]
INTERNAL_IPS = ('127.0.0.1',)

## Pacote necessario para o cache: python-memcached.noarch
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

try:
    from .local_settings import *
except ImportError as e:
    pass
