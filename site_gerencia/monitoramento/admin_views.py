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

def html_render(items):
    try:
        return "<ul><li>"+str(items.next())+'</li>'+html_render(items)+'</ul>'
    except StopIteration:
        return ''

def __get_object_str(curr_object):
    obj_type = str(type(curr_object))
    obj_type = obj_type.split("'")[1]
    obj_type = obj_type.split('.').pop()
    object_representative = eval(obj_type+'_representative')
    new_object = object_representative(original_obj=curr_object)
    obj_str = new_object.to_string()

    if obj_str is None:
        obj_str = str(curr_object)

    return obj_str

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
            #next_source = ch.source
            #aux_list = []
            #aux_list_html = []
            #while True:

            #    obj_str = __get_object_str(next_source)

            #    #aux_list.append(cgi.escape('((%s/%s))' %
            #    #    (next_source, type(next_source))))
            #    aux_list.append(cgi.escape(obj_str))
            #    if hasattr(next_source, 'sink'):
            #        next_source = next_source.sink
            #    else:
            #        break

            #aux_list.reverse()
            #html = html_render(iter(aux_list))

            object_r = __get_representative_object(ch.source)
            #ch_r = MulticastOutput_representative(original_obj=ch.source)
            #html = ch_r.to_html()
            html = object_r.to_html()

            channel_data = {
                'name': ch.name,
                'number': ch.number,
                'html_tree': html,
                #'sink_list': aux_list,
            }
            channel_list.append(channel_data)


    response = render_to_response("admin/mon.html",
        { 'title': 'Monitoramento', 'mon_servers': mon_servers,
        'channel_list': channel_list,
        }, context_instance=RequestContext(request))
    return response


