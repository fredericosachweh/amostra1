# -*- encoding:utf-8 -*-

import sys
import os

from settings import *

print('SETTINGS: CLAUDIO ;-)')

DEBUG = True

if 'test' in sys.argv:
    print('SETTINGS: TESTE SQLITE')
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
    print('SETTINGS: DATABASE MYSQL')
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


