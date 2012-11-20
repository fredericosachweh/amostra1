# Create your views here.



import netsnmp
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta

from device.models import Server
from tv.models import Channel

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
    html_list = []
    for ch in channels:
        if hasattr(ch, 'source'):
            next_source = ch.source
            aux_list = []
            aux_list_html = []
            while True:
                aux_list.append(cgi.escape('((%s/%s))' %
                    (next_source, type(next_source))))
                if hasattr(next_source, 'sink'):
                    next_source = next_source.sink
                else:
                    break

            aux_list.append(cgi.escape(' ## %s ## == %s' % (ch, type(ch) )))
            aux_list.reverse()
            channel_list.append(aux_list)

            html = html_render(iter(aux_list))
            html_list.append(html)

            sys.stdout.flush()

    resposta = render_to_response("admin/mon.html",
        { 'title': 'Monitoramento', 'mon_servers': mon_servers,
        'channel_list': channel_list, 'html_list': html_list,
        }, context_instance=RequestContext(request))
    return resposta


