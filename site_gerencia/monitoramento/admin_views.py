# Create your views here.

import netsnmp
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta

from device.models import Server
from tv.models import Channel

from models import *

from pprint import pprint
import sys
import cgi

def _get_snmp_status(server=None):
    if server is None:
        return None

    community = 'mmmcast'
    ver = 1
    port = 161
    host = server
    bind1 = netsnmp.Varbind('sysUpTime.0')
    snmpget = netsnmp.snmpget(bind1,
                        Version=ver,
                        RemotePort=port,
                        DestHost=host,
                        Community=community,
                        Timeout=1000000,
                        Retries=1
                        )
    uptime_all = snmpget[0]
    if uptime_all is None:
        return None
    else:
        uptime_seconds = int(uptime_all)/100
        uptime = timedelta(seconds=int(uptime_seconds))
        uptime_h = timedelta(seconds=int(uptime.seconds))
        return [int(uptime.days), str(uptime_h)]

def __get_representative_object(curr_object):
    obj_type = str(type(curr_object))
    obj_type = obj_type.split("'")[1]
    obj_type = obj_type.split('.').pop()
    object_representative = eval(obj_type+'_representative')
    new_object = object_representative(original_obj=curr_object)

    return new_object

def mon_list(request):
    servers = Server.objects.all()
    mon_servers = []
    for server in servers:
        server_data = {}
        server_data['id']   = server.id
        server_data['status'] = _get_snmp_status(server.host)
        server_data['host']   = server.host
        server_data['name']   = server.name
        mon_servers.append(server_data)
        del(server_data)

    channels = Channel.objects.all()
    channel_list = []
    for ch in channels:
        if hasattr(ch, 'source'):
            object_r = __get_representative_object(ch.source)
            #html = object_r.to_html_tree()
            html = object_r.to_html_linear()

            channel_data = {
                'name': ch.name,
                'number': ch.number,
                'html_tree': html,
            }
            channel_list.append(channel_data)


    response = render_to_response("admin/mon.html",
        { 'title': 'Monitoramento', 'mon_servers': mon_servers,
        'channel_list': channel_list,
        }, context_instance=RequestContext(request))
    return response


