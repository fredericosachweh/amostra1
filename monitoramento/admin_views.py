# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta
from django.conf import settings

#from models import MonServer
from tv.models import Channel

from models import *
from django.views.generic.simple import direct_to_template


def dashboard(request):
    monitoring_servers = MonServer.objects.filter(server_type='monitor')
    response = render_to_response("admin/monitoring/dashboard.html",
        {'monitoring_servers': monitoring_servers,
        }, context_instance=RequestContext(request))
    return response


def channel_tree(request):
    tree_type = request.path.split('/')
    tree_request = tree_type.pop()
    if tree_request == '':
        tree_request = tree_type.pop()
    if tree_request == 'channel_tree_status':
        show_status = True
    else:
        show_status = False

    servers = Server.objects.all()

    server_dot_cluster = {}
    for server in servers:
        server_dot_cluster[server.name] = pydot.Cluster(
            graph_name=server.name, rankdir="LR",
            label="server: " + server.name, fontsize=20)

    channels = Channel.objects.all()
    roots = []
    for ch in channels:
        if hasattr(ch, 'source'):
            object_r = get_representative_object(ch.source)
            root = object_r.get_root()
            if (root is not None) and (root not in roots):
                roots.append(root)

    MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
    GRAPH_ROOT = os.path.join(MEDIA_ROOT, 'mon/roots')
    if os.path.exists(GRAPH_ROOT) == False:
        os.makedirs(GRAPH_ROOT)
    root_graph = []

    NUM = 1
    for root in roots:
        graph = pydot.Dot(graph_type='digraph', splines='spline')
        object_r = get_representative_object(root)
        graph = object_r.to_graph(graph, server_dot_cluster,
        with_status=show_status)
        for n, cluster in server_dot_cluster.iteritems():
            graph.add_subgraph(cluster)
        graph_name = 'graph%d.png' % NUM
        graph_file = os.path.join(GRAPH_ROOT, graph_name)
        graph.write_png(graph_file)
        root_graph.append(graph_name)

        NUM += 1

        del(server_dot_cluster)
        server_dot_cluster = {}
        for server in servers:
            server_dot_cluster[server.name] = pydot.Cluster(
                graph_name=server.name, rankdir="LR",
                label="server: " + server.name, fontsize=20)

    response = render_to_response("admin/monitoring/tree.html",
        {'title': 'Monitoramento', 'root_graph': root_graph,
        }, context_instance=RequestContext(request))
    return response


def mon_export(request):
    nagios_config = NagiosConfig()

    if nagios_config.set_monitor_servers() is False:
        error_msg = "Nao existe nenhum servidor de monitoramento configurado!"
        return render_to_response("admin/monitoring/export_error.html",
            {'title': 'Monitoramento: exportar CFG', 'error_msg': error_msg,
            }, context_instance=RequestContext(request))

    if nagios_config.export_cfg() is False:
        error_msg = "Problema ao exportar configuracao!!!"
        return render_to_response("admin/monitoring/export_error.html",
            {'title': 'Monitoramento: exportar CFG', 'error_msg': error_msg,
            }, context_instance=RequestContext(request))

    if nagios_config.copy_cfg() is False:
        error_msg = "Problema ao copiar a configuracao para o servidor de monitoramento!!!"
        return render_to_response("admin/monitoring/export_error.html",
            {'title': 'Monitoramento: exportar CFG', 'error_msg': error_msg,
            }, context_instance=RequestContext(request))

    if nagios_config.nagios_validate() is False:
        error_msg = "Configuracao do Nagios com problemas!!!"
        return render_to_response("admin/monitoring/export_error.html",
            {'title': 'Monitoramento: exportar CFG', 'error_msg': error_msg,
            }, context_instance=RequestContext(request))

    if nagios_config.nagios_reload() is False:
        error_msg = "Problema ao recarregar o nagios!!!"
        return render_to_response("admin/monitoring/export_error.html",
            {'title': 'Monitoramento: exportar CFG', 'error_msg': error_msg,
            }, context_instance=RequestContext(request))

    response = render_to_response("admin/monitoring/export.html",
        {'title': 'Monitoramento: exportar CFG',
        }, context_instance=RequestContext(request))
    return response
