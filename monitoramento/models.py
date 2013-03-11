from django.db import models
from django.db.models.signals import post_save

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

from cgi import escape
import pydot


from django.dispatch import receiver
import os
import logging

import pynag.Model

#@receiver(post_save, sender=Server)
#def Server_enable_mon(sender, instance, created, **kwargs):
#
#    if created is False:
#        return
#
#    MONITOR_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
#    MONITOR_CONFS = os.path.join(MONITOR_ROOT_PATH, 'conf_templates')
#    DVB_SNMP_CONF = 'DVB_snmpd.conf'
#
#    if instance.server_type == 'dvb':
#        #from tempfile import NamedTemporaryFile
#
#        local_file = os.path.join(MONITOR_CONFS, DVB_SNMP_CONF)
#        log = logging.getLogger('debug')
#        log.info("Novo servidor DVB: [%s], adicionando config SNMP", instance)
#        log.info(" => Arquivo de configuracao %s", local_file)
#        remote_tmpfile = instance.create_tempfile()
#        instance.put(local_file, remote_tmpfile)
#        instance.execute('/usr/bin/sudo /bin/cp -f %s ' \
#            '/etc/snmp/snmpd.conf' % remote_tmpfile)
#        instance.execute('/usr/bin/sudo /bin/systemctl restart snmpd.service')

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

    def to_graph(self, pydot_obj, cluster_dict):
        if type(pydot_obj) != pydot.Dot:
            return

        graph = pydot_obj

        my_node = pydot.Node(style="filled")
        my_node.set_name(self.to_string(show_info=False))
        if hasattr(self.original_obj, 'running'):
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
                graph = object_representative.to_graph(graph, cluster_dict)

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
