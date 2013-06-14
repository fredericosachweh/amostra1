#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save

from device.models import AbstractServer
from device.models import Server
from device.models import NIC
from device.models import UniqueIP
from device.models import DeviceServer
from device.models import Antenna
from device.models import DemuxedService
from device.models import DigitalTunerHardware
from device.models import DvbTuner #  DVBS
from device.models import IsdbTuner # DVBT
from device.models import UnicastInput
from device.models import MulticastInput
from device.models import FileInput
from device.models import MulticastOutput
from device.models import StreamRecorder
from device.models import StreamPlayer
from device.models import SoftTranscoder
from tv.models import Channel
from django.conf import settings
from types import ListType
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from cgi import escape
import pydot


from django.dispatch import receiver
import os
import logging

import pynag.Model
import pynag.Parsers
import shutil
import os.path





class MonServer(AbstractServer):
    """
    Servidor de monitoramento herdado do device.Sercer
    """
    http_port = models.PositiveSmallIntegerField(_(u'Porta HTTP'),
        blank=True, null=True, default=80)
    http_username = models.CharField(_(u'Usuário HTTP'), max_length=200, blank=True)
    http_password = models.CharField(_(u'Senha HTTP'), max_length=200, blank=True)
    SERVER_TYPE_CHOICES = [(u'monitor', _(u'Servidor Monitoramento')),]
    server_type = models.CharField(_(u'Tipo de Servidor'), max_length=100,
                                   choices=SERVER_TYPE_CHOICES)

    class Meta:
        #db_table = 'monitor_server'
        verbose_name = _(u'Servidor de monitoramento')
        verbose_name_plural = _(u'Servidores de monitoramento')

    def __init__(self, *args, **kwargs):
        super(MonServer, self).__init__(*args, **kwargs)
        self.server_type = u'monitor'

    def switch_link(self):
        url = reverse('monitoramento.views.monserver_status', kwargs={'pk': self.id})
        return '<a href="%s" id="server_id_%s" >Atualizar</a>' % (url, self.id)

    switch_link.allow_tags = True
    switch_link.short_description = u'Status'


def get_representative_object(curr_object):
    obj_type = str(type(curr_object))
    obj_type = obj_type.split("'")[1]
    obj_type = obj_type.split('.').pop()
    object_representative = eval(obj_type+'_representative')
    new_object = object_representative(original_obj=curr_object)

    return new_object

class NagiosConfig:
    monitoring_servers = []
    cfg_files = []

    def set_monitor_servers(self):
        servers = Server.objects.all()
        for server in servers:
            if server.server_type == "monitor":
                self.monitoring_servers.append(server)
        if len(self.monitoring_servers) == 0:
            return False
        else:
            return True

    def create_file(self, file_name):
        f = open(file_name, 'w')
        f.close()

    def export_cfg(self):
        try:
            CFG_ROOT = '/tmp/monitoramento/nagios'
            if os.path.exists(CFG_ROOT) == True:
                shutil.rmtree(CFG_ROOT)

            os.makedirs(CFG_ROOT)
            CFG_HOST_FILE = os.path.join(CFG_ROOT, 'hosts.cfg')
            self.cfg_files.append(CFG_HOST_FILE)
            CFG_SERVICE_FILE = os.path.join(CFG_ROOT, 'services.cfg')
            self.cfg_files.append(CFG_SERVICE_FILE)
            CFG_SERVICEGROUP_FILE = os.path.join(CFG_ROOT, 'servicegroups.cfg')
            self.cfg_files.append(CFG_SERVICEGROUP_FILE)

            for file_name in self.cfg_files:
                self.create_file(file_name)

            CFG_TMP_FILE = os.path.join(CFG_ROOT, 'tmp.cfg')
            self.create_file(CFG_TMP_FILE)

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
                    object_r = get_representative_object(ch.source)
                    sid = object_r.get_channel_sid()
                    object_r.to_pynag_service(service_group = \
                        service_group_name,
                        cfg_file = CFG_SERVICE_FILE, sid = sid)
            return True

        except Exception, e:
            print str(e)
            return False

    def copy_cfg(self):
        try:
            for server in self.monitoring_servers:
                for cfg_file in self.cfg_files:
                    file_name = os.path.basename(cfg_file)
                    remote_file = "/etc/nagios/iptv/%s" % file_name
                    server.put(cfg_file, remote_file)
                    cmd = '/usr/bin/sudo /bin/chown nagios.nagios'
                    server.execute('%s %s' % (cmd, remote_file))
            return True
        except Exception, e:
            print str(e)
            return False

    def nagios_validate(self):
        try:
            cmd = '/usr/bin/sudo /usr/sbin/nagios -v /etc/nagios/nagios.cfg'
            for server in self.monitoring_servers:
            	server.execute('%s' % cmd)
        except Exception, e:
            print str(e)
            return False

    def nagios_reload(self):
        try:
            cmd = '/usr/bin/sudo /bin/systemctl restart nagios.service'
            for server in self.monitoring_servers:
            	server.execute('%s' % cmd)
        except Exception, e:
            print str(e)
            return False


class BaseRepresentative(object):
    def __init__(self, *args, **kwargs):
        try:
            self.original_obj = kwargs['original_obj']
        except KeyError:
            self.original_obj = None

    def obj_validate(self, obj_type):
        response = False
        if self.original_obj is not None:
            obj_type = str(type(self.original_obj))
            obj_type = obj_type.split("'")[1]
            if obj_type.split('.').pop() == obj_type:
                response = True

        return response

    def to_pynag_service(self, service_group=None, cfg_file=None, sid=None):
        monitored_services_list = ['MulticastOutput', 'UniqueIP',
            'MulticastInput', 'DvbTuner' ]
        #monitored_services_list = ['DvbTuner' ]

        def create_service(defined_service_group=None, defined_cfg_file=None,
                obj_type = None):
            server = self.get_server()
            service_name = self.to_pynag_string()

            pynag.Model.cfg_file = defined_cfg_file
            service_check = pynag.Model.Service.objects.filter(
                    host_name = server.name.lower(),
                    service_description = service_name)

            if len(service_check) > 0:
                service = service_check[0]
            else:
                service = pynag.Model.Service()
                service.host_name = server.name.lower()
                service.service_description = service_name
                #service.attribute_appendfield('servicegroups',
                #    defined_service_group)
                service.use = 'iptv_service'
                if obj_type == 'DvbTuner':
                    adapter_hw = self.original_obj.adapter
                    service.check_command = 'check_dvb!%s' % adapter_hw
                else:
                    ip = str(self.original_obj.ip)
                    port = str(self.original_obj.port)
                    service.check_command = 'check_tsprobe!%s!%s!%s' % (
                        ip, port, str(sid))

            service.add_to_servicegroup(defined_service_group)
            service.set_filename(defined_cfg_file)

            service.save()

        if (cfg_file is None) or (sid is None):
            return

        this_obj_type = str(type(self.original_obj))
        this_obj_type = this_obj_type.split("'")[1]
        this_obj_type = this_obj_type.split('.').pop()

        if this_obj_type in monitored_services_list:
            create_service(defined_service_group = service_group,
                    defined_cfg_file = cfg_file, obj_type = this_obj_type)

        if hasattr(self.original_obj, 'sink'):
            sink_object = self.original_obj.sink
            obj_type = str(type(sink_object))
            obj_type = obj_type.split("'")[1]
            obj_type = obj_type.split('.').pop()
            object_representative = eval(obj_type+'_representative')
            sink_object_representative = object_representative(
                original_obj = sink_object)

            sink_object_representative.to_pynag_service(
            service_group = service_group, cfg_file = cfg_file, sid = sid)

        return

    def to_html_tree(self):
        sink_object_html = ''
        if hasattr(self.original_obj, 'sink'):
            sink_object = self.original_obj.sink
            obj_type = str(type(sink_object))
            obj_type = obj_type.split("'")[1]
            obj_type = obj_type.split('.').pop()
            object_representative = eval(obj_type+'_representative')
            sink_object_representative = object_representative(
                original_obj = sink_object)
            sink_object_html = sink_object_representative.to_html_tree()

        return "<ul><li>"+escape(self.to_string())+'</li>'+sink_object_html+'</ul>'

    def to_html_linear(self):
        sink_object_html = ''
        object_html = escape(self.to_string())

        if hasattr(self.original_obj, 'sink'):
            sink_object = self.original_obj.sink
            obj_type = str(type(sink_object))
            obj_type = obj_type.split("'")[1]
            obj_type = obj_type.split('.').pop()
            object_representative = eval(obj_type+'_representative')
            sink_object_representative = object_representative(
                original_obj = sink_object)
            sink_object_html = sink_object_representative.to_html_linear()

        if hasattr(self.original_obj, 'status'):
            object_html += '&nbsp;STATUS:'
            if self.original_obj.status:
                object_html +='<img alt="Running" src="'+settings.STATIC_URL+'admin/img/green-ok.gif">'
            else:
                object_html +='<img alt="Error" src="'+settings.STATIC_URL+'admin/img/red-error.gif">'

        return '<div class="html_linear" >'+object_html+'</div>'+sink_object_html

    def to_pynag_string(self):
        return self.to_string(show_info=False)

    def to_string(self,show_info=True):
        obj_type = str(type(self))
        return 'to_string: Not implemented in %s' % (obj_type.split("'")[1])

    def to_xml(self):
        obj_type = str(type(self))
        return 'to_xml: Not implemented in %s' % (obj_type.split("'")[1])

    def to_json(self):
        obj_type = str(type(self))
        return 'to_json: Not implemented in %s' % (obj_type.split("'")[1])

    def to_html_root(self):
        object_html = ''
        if hasattr(self.original_obj, 'src'):
            if type(self.original_obj.src) == ListType:
                child_list = self.original_obj.src
            else:
                child_list = self.original_obj.src.select_related()

            for child_object in child_list:
                obj_type = str(type(child_object))
                obj_type = obj_type.split("'")[1]
                obj_type = obj_type.split('.').pop()
                object_representative = eval(obj_type+'_representative')
                object_representative = object_representative(
                    original_obj = child_object)
                object_html += object_representative.to_html_root()

        return "<ul><li>"+escape(self.to_string())+'</li>'+object_html+'</ul>'

    def to_graph(self, pydot_obj, cluster_dict, with_status=False):
        if type(pydot_obj) != pydot.Dot:
            return

        graph = pydot_obj

        my_node = pydot.Node(style="filled")
        my_node.set_name(self.to_string(show_info=False))
        if hasattr(self.original_obj, 'running'):
            if with_status is True:
                if self.original_obj.running():
                    my_node.set_fillcolor("green")
                else:
                    my_node.set_fillcolor("red")
            else:
                my_node.set_fillcolor("blue")

        server = self.get_server()

        if server is not None:
            cluster = cluster_dict[server.name]
            cluster.add_node(my_node)
        else:
            graph.add_node(my_node)

        if hasattr(self.original_obj, 'src'):
            if type(self.original_obj.src) == ListType:
                child_list = self.original_obj.src
            else:
                child_list = self.original_obj.src.select_related()

            for child_object in child_list:
                obj_type = str(type(child_object))
                obj_type = obj_type.split("'")[1]
                obj_type = obj_type.split('.').pop()
                object_representative = eval(obj_type+'_representative')
                object_representative = object_representative(
                    original_obj = child_object)

                child_node = pydot.Node(style="filled")
                child_node.set_name(
                    object_representative.to_string(show_info=False))
                graph.add_node(child_node)
                edge = pydot.Edge(
                    my_node,
                    child_node)
                graph.add_edge(edge)
                graph = object_representative.to_graph(graph, cluster_dict,
                with_status)

        if hasattr(self.original_obj, 'channel'):
            child_object = self.original_obj.channel
            if child_object is not None:
                obj_type = str(type(child_object))
                obj_type = obj_type.split("'")[1]
                obj_type = obj_type.split('.').pop()
                object_representative = eval(obj_type+'_representative')
                object_representative = object_representative(
                    original_obj = child_object)

                child_node = pydot.Node(style="filled")
                child_node.set_name(
                    object_representative.to_string(show_info=False),
                    )


                graph.add_node(child_node)
                edge = pydot.Edge(
                    my_node,
                    child_node)

                graph.add_edge(edge)
                graph = object_representative.to_graph(graph, cluster_dict)

        return graph

    def get_root(self):
        sink_object = self.original_obj
        while True:
            if hasattr(sink_object, 'sink'):
                #if sink_object.sink != None:
                sink_object = sink_object.sink
            else:
                break
        return sink_object

    def get_server(self):
        sink_object = self.original_obj
        server_object = None
        while True:
            if hasattr(sink_object, 'server'):
                server_object = sink_object.server
                break
            else:
                if hasattr(sink_object, 'sink'):
                    sink_object = sink_object.sink
                elif hasattr(sink_object, 'source'):
                    sink_object = sink_object.source
                else:
                    break

        return server_object

    def get_channel_sid(self):
        sid = None
        sink_object = self.original_obj
        while True:
            obj_type = str(type(sink_object))
            obj_type = obj_type.split("'")[1] 
            obj_type = obj_type.split('.').pop()
            if obj_type == 'DemuxedService':
                sid = int(sink_object.sid)
                break
            else:
                if hasattr(sink_object, 'sink'):
                    sink_object = sink_object.sink
                elif hasattr(sink_object, 'source'):
                    sink_object = sink_object.source
                else:
                    break

        return sid


class Server_representative(BaseRepresentative):
    pass

class NIC_representative(BaseRepresentative):
    pass

class UniqueIP_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(UniqueIP_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('UniqueIP'):
            return None

    def to_pynag_string(self):
        return_string = 'UniqueIP_%s:%d' % (
            self.original_obj.ip, self.original_obj.port)
        if hasattr(self.original_obj.sink, "nic_src"):
            if type(self.original_obj.sink.nic_src) == NIC:
                return_string = "%s [iface: %s]" % (
                    return_string, self.original_obj.sink.nic_src.name)
        return return_string

    def to_string(self, show_info=True):
        if hasattr(self.original_obj.sink, 'server'):
            return_string = 'UniqueIP: %s:%d [server: %s]' % (
                self.original_obj.ip, self.original_obj.port,
                self.original_obj.sink.server.name)
        else:
            return_string = 'UniqueIP: %s:%d' % (
                self.original_obj.ip, self.original_obj.port)
        if hasattr(self.original_obj.sink, "nic_src"):
            if type(self.original_obj.sink.nic_src) == NIC:
                return_string = "%s [iface: %s - ip: %s]" % (
                    return_string, self.original_obj.sink.nic_src.name,
                    self.original_obj.sink.nic_src.ipv4)
        return return_string

class DeviceServer_representative(BaseRepresentative):
    pass

class Dvblast_representative(BaseRepresentative):
    pass

class Antenna_representative(BaseRepresentative):
    pass

class DemuxedService_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(DemuxedService_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('DemuxedService'):
            return None

    def to_string(self, show_info=True):
        return_string = 'DemuxedService: %s %s (SID:%d) [server: %s]' % (
            self.original_obj.provider,
            self.original_obj.service_desc,
            self.original_obj.sid,
            self.original_obj.server.name )
        return return_string

class DigitalTunerHardware_representative(BaseRepresentative):
    pass

class DvbTuner_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(DvbTuner_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('DvbTuner'):
            return None

    def to_pynag_string(self):
        return_string = 'DVB_Tuner_%s' % (self.original_obj.adapter)
        return return_string

    def to_string(self, show_info=True):
        return_string = 'DVB Tuner: [%s] (%s - %d %s %d [server: %s])' % (
            self.original_obj.adapter, self.original_obj.antenna.satellite,
            self.original_obj.frequency, self.original_obj.polarization,
            self.original_obj.symbol_rate,
            self.original_obj.server.name)
        return return_string


class IsdbTuner_representative(BaseRepresentative):
    pass


class UnicastInput_representative(BaseRepresentative):
    pass


class MulticastInput_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(MulticastInput_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('MulticastInput'):
            return None

    def to_pynag_string(self):
        return_string = 'MulticastInput_%s:%d_%s' % (
            self.original_obj.ip, self.original_obj.port,
            self.original_obj.interface.name)
        return return_string

    def to_string(self, show_info=True):
        return_string = 'MulticastInput: %s:%d (%s %s [server: %s])' % (
            self.original_obj.ip, self.original_obj.port,
            self.original_obj.interface.name,
            self.original_obj.interface.ipv4,
            self.original_obj.interface.server.name)
        return return_string

class FileInput_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(FileInput_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('FileInput'):
            return None

    def to_string(self, show_info=True):
        filename = self.original_obj.filename.split('/')
        return_string = 'FileInput: %s (%s) [server: %s])' % (
            self.original_obj.description,
            filename.pop(),
            self.original_obj.server.name,
            )
        return return_string

class MulticastOutput_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(MulticastOutput_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('MulticastOutput'):
            return None

    def to_pynag_string(self):
        return_string = 'MulticastOutput_%s:%d_%s' % (
            self.original_obj.ip, self.original_obj.port,
            self.original_obj.interface.name)
        return return_string

    def to_string(self, show_info=True):
        return_string = 'MulticastOutput: %s:%d (%s %s [server: %s])' % (
            self.original_obj.ip, self.original_obj.port,
            self.original_obj.interface.name,
            self.original_obj.interface.ipv4,
            self.original_obj.interface.server.name)
        return return_string

class StreamRecorder_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(StreamRecorder_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('StreamRecorder'):
            return None

    def to_string(self, show_info=True):
        #return_string = 'Channel: %d - %s' % (
        #    self.original_obj.number,
        #    self.original_obj.name,
        #    )
        return "Recorder: "+str(self.original_obj)
    pass

class StreamPlayer_representative(BaseRepresentative):
    pass

class SoftTranscoder_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(SoftTranscoder_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('SoftTranscoder'):
            return None

    def to_string(self, show_info=True):
        return_string = 'SoftTranscoder: [%s] Gain:%s - Normalize:%s - Compress:%s' % (
            self.original_obj.audio_codec,
            str(self.original_obj.apply_gain),
            str(self.original_obj.apply_normvol),
            str(self.original_obj.apply_compressor),
            )
        return return_string

class Channel_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(Channel_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('Channel'):
            return None

    def to_string(self, show_info=True):
        return_string = 'Channel: %d - %s' % (
            self.original_obj.number,
            self.original_obj.name,
            )
        return return_string

class RealTimeEncrypt_representative(BaseRepresentative):
    pass
