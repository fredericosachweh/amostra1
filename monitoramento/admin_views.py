# Create your views here.

import netsnmp
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta
from django.conf import settings

import os.path

from device.models import Server
from tv.models import Channel

import pynag.Model
import pynag.Parsers
import shutil

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


def mon_export(request):
    def create_file(file_name):
        f = open(file_name, 'w')
        f.close()

    MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
    CFG_ROOT = os.path.join(MEDIA_ROOT, 'mon/nagios')
    if os.path.exists(CFG_ROOT) == True:
        shutil.rmtree(CFG_ROOT)

    os.makedirs(CFG_ROOT)
    CFG_HOST_FILE = os.path.join(CFG_ROOT, 'hosts.cfg')
    CFG_SERVICE_FILE = os.path.join(CFG_ROOT, 'services.cfg')
    CFG_SERVICEGROUP_FILE = os.path.join(CFG_ROOT, 'servicegroups.cfg')
    CFG_TMP_FILE = os.path.join(CFG_ROOT, 'tmp.cfg')

    create_file(CFG_HOST_FILE)
    create_file(CFG_SERVICE_FILE)
    create_file(CFG_SERVICEGROUP_FILE)
    create_file(CFG_TMP_FILE)

    f = open(CFG_TMP_FILE, 'w')
    f.write('cfg_file=%s\n' % CFG_HOST_FILE )
    f.write('cfg_file=%s\n' % CFG_SERVICE_FILE )
    f.write('cfg_file=%s\n' % CFG_SERVICEGROUP_FILE )
    f.close()

    pynag.Model.cfg_file = CFG_TMP_FILE
    config = pynag.Parsers.config(cfg_file = CFG_TMP_FILE)
    config.parse()
    pynag.Model.config = config


    service_template = pynag.Model.Service()
    service_template.name = 'iptv_service'
    service_template.active_checks_enabled = 1
    service_template.passive_checks_enabled = 1
    service_template.obsess_over_service = 0
    service_template.check_freshness = 0
    service_template.notifications_enabled = 0
    service_template.event_handler_enabled = 1
    service_template.flap_detection_enabled = 1
    service_template.process_perf_data = 1
    service_template.retain_status_information = 1
    service_template.retain_nonstatus_information = 0
    service_template.register = 0
    service_template.is_volatile = 0
    service_template.check_period = '24x7'
    service_template.max_check_attempts = 5
    service_template.normal_check_interval = 5
    service_template.retry_check_interval = 3
    #service_template.contact_groups = 'idatacenter'
    service_template.notification_interval = 0
    service_template.notification_period = '24x7'
    service_template.notification_options = 'c,r'
    service_template.action_url = '/pnp4nagios/graph?host=$HOSTNAME$&srv=$SERVICEDESC$'
    service_template.set_filename(CFG_SERVICE_FILE)
    service_template.save()
    del(service_template)



    host_template = pynag.Model.Host()
    host_template.name = 'iptv_server'
    host_template.event_handler_enabled = 1
    host_template.flap_detection_enabled = 1
    host_template.max_check_attempts = 3
    #host_template.contact_groups = idatacenter
    host_template.notification_options = 'd,r'
    host_template.notification_interval = 0
    host_template.notification_period = '24x7'
    host_template.check_period = '24x7'
    host_template.notifications_enabled = 0
    host_template.process_perf_data = 1
    host_template.active_checks_enabled = 1
    host_template.passive_checks_enabled = 1
    host_template.register = 0
    host_template.action_url = '/pnp4nagios/graph?host=$HOSTNAME$'
    host_template.set_filename(CFG_HOST_FILE)
    host_template.save()
    del(host_template)

    pynag.Model.cfg_file = CFG_TMP_FILE
    config = pynag.Parsers.config(cfg_file = CFG_TMP_FILE)
    config.parse()
    pynag.Model.config = config

    servers = Server.objects.all()
    for server in servers:
        my_host = pynag.Model.Host()
        my_host.use = 'iptv_server'
        my_host.host_name = server.name.lower()
        my_host.alias = server.name.upper()
        my_host.address = server.host
        my_host.check_command = 'check-host-alive'
        my_host.set_filename(CFG_HOST_FILE)
        my_host.save()
        del(my_host)

        service_cpu = pynag.Model.Service()
        service_cpu.service_description = 'CPU'
        service_cpu.use = 'iptv_service'
        service_cpu.host_name = server.name.lower()
        service_cpu.set_filename(CFG_SERVICE_FILE)
        #TODO: Coletar a community SNMP da config ou do model de monitoramento
        service_cpu.check_command = 'snmp_cpu_total!mmmcast!85!95'
        service_cpu.save()
        del(service_cpu)


    channels = Channel.objects.all()
    for ch in channels:
        service_group_name = '%d-%s' % (
                ch.number, ch.name.replace(' ','_'))
        service_group = pynag.Model.Servicegroup()
        service_group.servicegroup_name = service_group_name
        service_group.alias = "Canal %d - %s" % (
                ch.number, ch.name)
        service_group.set_filename(CFG_SERVICEGROUP_FILE)
        service_group.save()
        del(service_group)

        if hasattr(ch, 'source'):
            object_r = __get_representative_object(ch.source)
            sid = object_r.get_channel_sid()
            object_r.to_pynag_service(service_group = service_group_name,
                    cfg_file = CFG_SERVICE_FILE, sid = sid)

    response = render_to_response("admin/mon.html",
        { 'title': 'Monitoramento: exportar CFG',
        }, context_instance=RequestContext(request))
    return response
