# Create your views here.

import netsnmp
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta
from django.conf import settings

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
    server_dot_cluster = {}
    for server in servers:
        server_dot_cluster[server.name] = pydot.Cluster(
            graph_name=server.name, rankdir="LR",
            label="server: "+server.name, fontsize=20)
        #server_data = {}
        #server_data['id']   = server.id
        #server_data['status'] = _get_snmp_status(server.host)
        #server_data['host']   = server.host
        #server_data['name']   = server.name
        #mon_servers.append(server_data)
        #del(server_data)


    channels = Channel.objects.all()
    channel_list = []
    roots = []
    for ch in channels:
        if hasattr(ch, 'source'):
            object_r = __get_representative_object(ch.source)
            #html = object_r.to_html_tree()
            #html = object_r.to_html_linear()

            root = object_r.get_root()
            if (root is not None) and (root not in roots):
                roots.append(root)

            #channel_data = {
            #    'name': ch.name,
            #    'number': ch.number,
            #    'html_tree': html,
            #}
            #channel_list.append(channel_data)


    MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
    GRAPH_ROOT = os.path.join(MEDIA_ROOT, 'mon/roots')
    if os.path.exists(GRAPH_ROOT) == False:
        os.makedirs(GRAPH_ROOT)

    root_graph = []

    NUM = 1
    for root in roots:
        graph = pydot.Dot(graph_type='digraph', splines='spline')
        #graph.set_node_defaults(shape='circle', fontsize=24)
        object_r = __get_representative_object(root)
        graph = object_r.to_graph(graph, server_dot_cluster)
        for name, cluster in server_dot_cluster.iteritems():
            graph.add_subgraph(cluster)
        graph_name = 'graph%d.png' % NUM
        graph_file = os.path.join(GRAPH_ROOT, graph_name)
        graph.write_png(graph_file)
        root_graph.append(graph_name)
        #graph.write('graph%d.dotfile' % NUM, format='raw', prog='dot')
        #graph.write_svg('graph%d.svg' % NUM)

        NUM += 1

        del(server_dot_cluster)
        server_dot_cluster = {}
        for server in servers:
            server_dot_cluster[server.name] = pydot.Cluster(
                graph_name=server.name, rankdir="LR",
                label="server: "+server.name, fontsize=20)


    response = render_to_response("admin/mon.html",
        { 'title': 'Monitoramento', 'mon_servers': mon_servers,
        'channel_list': channel_list, 'root_graph': root_graph,
        }, context_instance=RequestContext(request))
    return response


