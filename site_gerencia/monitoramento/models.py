from django.db import models
from django.db.models.signals import post_save

from device.models import Server
from device.models import NIC
from device.models import UniqueIP
from device.models import DeviceServer
from device.models import Dvblast
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

from cgi import escape


from django.dispatch import receiver
import os
import logging

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

    def to_string(self):
        return None

    def to_xml(self):
        return None

    def to_json(self):
        return None

class Server_representative(BaseRepresentative):
    pass

class NIC_representative(BaseRepresentative):
    pass

class UniqueIP_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(UniqueIP_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('UniqueIP'):
            return None

    def to_string(self):
        return_string = 'UniqueIP: %s:%d' % (
            self.original_obj.ip, self.original_obj.port)
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

    def to_string(self):
        return_string = 'DemuxedService: SID=%d (from MPEG TS)' % (
            self.original_obj.sid )
        return return_string

class DigitalTunerHardware_representative(BaseRepresentative):
    pass

class DvbTuner_representative(BaseRepresentative):
    pass

class IsdbTuner_representative(BaseRepresentative):
    pass

class UnicastInput_representative(BaseRepresentative):
    pass

class MulticastInput_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(MulticastInput_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('MulticastInput'):
            return None

    def to_string(self):
        return_string = 'MulticastInput: %s:%d (%s %s [%s])' % (
            self.original_obj.ip, self.original_obj.port,
            self.original_obj.interface.name,
            self.original_obj.interface.ipv4,
            self.original_obj.interface.server.name )
        return return_string

class FileInput_representative(BaseRepresentative):
    pass

class MulticastOutput_representative(BaseRepresentative):
    def __init__(self, *args, **kwargs):
        super(MulticastOutput_representative, self).__init__(*args, **kwargs)
        if not self.obj_validate('MulticastOutput'):
            return None

    def to_string(self):
        return_string = 'MulticastOutput: %s:%d (%s %s [%s])' % (
            self.original_obj.ip, self.original_obj.port,
            self.original_obj.interface.name,
            self.original_obj.interface.ipv4,
            self.original_obj.interface.server.name )
        return return_string

class StreamRecorder_representative(BaseRepresentative):
    pass

class StreamPlayer_representative(BaseRepresentative):
    pass

class SoftTranscoder_representative(BaseRepresentative):
    pass

class Channel_representative(BaseRepresentative):
    pass
