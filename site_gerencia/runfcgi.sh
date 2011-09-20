#!/bin/bash

exec /usr/bin/env - \
  PYTHONPATH="../python:.." \
 ./manage.py runfcgi daemonize=true socket=/tmp/site_gerencia.sock maxrequests=1 debug=true --verbosity=2 --traceback
