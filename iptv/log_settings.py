
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
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
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
        },
        'file.stblog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/stblog.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.api': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/api.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.client': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/client.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.tvod': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/tvod.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.import_epg': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/import_epg.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.nbridge': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/nbridge.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.unittest': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/unittest.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
        'file.erp': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/erp.log' % IPTV_LOG_DIR,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file.debug'],
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
        },
        'stblog': {
            'handlers': ['file.stblog'],
            'level': 'DEBUG',
            'propagate': True
        },
        'api': {
            'handlers': ['file.api'],
            'level': 'DEBUG',
            'propagate': True
        },
        'client': {
            'handlers': ['file.client'],
            'level': 'DEBUG',
            'propagate': True
        },
        'tvod': {
            'handlers': ['file.tvod'],
            'level': 'DEBUG',
            'propagate': True
        },
        'epg_import': {
            'handlers': ['file.import_epg'],
            'level': 'DEBUG',
            'propagate': True
        },
        'nbridge': {
            'handlers': ['file.nbridge'],
            'level': 'DEBUG',
            'propagate': True
        },
        'unittest': {
            'handlers': ['file.unittest'],
            'level': 'DEBUG',
            'propagate': True
        },
        'erp': {
            'handlers': ['file.erp'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
