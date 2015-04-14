#!/bin/bash
# https://support.mailroute.net/entries/23079421-API-Part-1-Introduction-Authentication-Schema-and-Resources
# http://httpkit.com/resources/HTTP-from-the-Command-Line/

# Forma correta (HEAD):
/usr/bin/curl \
-H "Authorization: ApiKey helber:72644da2f714abda48dc2063119aaf361cfa0e42" \
http://127.0.0.1:8000/tv/device/server/7/coldstart/

# Ou (GET):
/usr/bin/curl \
http://127.0.0.1:8000/tv/device/server/7/coldstart/?api_key=72644da2f714abda48dc2063119aaf361cfa0e42
# Ou (GET):
/usr/bin/curl \
http://127.0.0.1:8000/tv/device/server/7/coldstart/?api_key=72644da2f714abda48dc2063119aaf361cfa0e42&username=helber
# Ou (POST):
/usr/bin/curl \
-X POST \
-d 'api_key=72644da2f714abda48dc2063119aaf361cfa0e42' \
-d 'username=helber' \
http://127.0.0.1:8000/tv/device/server/7/coldstart/

# Ou (POST):
/usr/bin/curl \
-X POST \
-d 'api_key=72644da2f714abda48dc2063119aaf361cfa0e42&username=helber' \
http://127.0.0.1:8000/tv/device/server/7/coldstart/

#/usr/bin/curl http://%(my_ip)s:%(my_port)s%(coldstart_url)s -d 'started=1'
#/usr/bin/curl http://%(my_ip)s:%(my_port)s%(coldstart_url)s -d 'stoped=1'
#/usr/bin/curl http://%(my_ip)s:%(my_port)s%(status_url)s
#ACTION=="add", SUBSYSTEM=="dvb", ENV{DVB_DEVICE_TYPE}=="frontend", RUN+="/usr/bin/curl http://%(my_ip)s:%(my_port)s%(add_url)s -d 'adapter_nr=%%k'" 
#ACTION=="remove", SUBSYSTEM=="dvb", ENV{DVB_DEVICE_TYPE}=="frontend", RUN+="/usr/bin/curl http://%(my_ip)s:%(my_port)s%(rm_url)s -d 'adapter_nr=%%k'"

