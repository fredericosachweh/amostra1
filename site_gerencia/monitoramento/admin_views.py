# Create your views here.



import netsnmp
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta

from device.models import Server

from pprint import pprint


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


    #return HttpResponse("Hello!")
    resposta = render_to_response("admin/mon.html",
        { 'title': 'Monitoramento', 'mon_servers': mon_servers,
        }, context_instance=RequestContext(request))
    return resposta


