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

from django.dispatch import receiver
import os
import logging


@receiver(post_save, sender=Server)
def Server_enable_mon(sender, instance, created, **kwargs):

    if created is False:
        return

    MONITOR_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    MONITOR_CONFS = os.path.join(MONITOR_ROOT_PATH, 'conf_templates')
    DVB_SNMP_CONF = 'DVB_snmpd.conf'

    if instance.server_type == 'dvb':
        #from tempfile import NamedTemporaryFile

        local_file = os.path.join(MONITOR_CONFS, DVB_SNMP_CONF)
        log = logging.getLogger('debug')
        log.info("Novo servidor DVB: [%s], adicionando config SNMP", instance)
        log.info(" => Arquivo de configuracao %s", local_file)
        remote_tmpfile = instance.create_tempfile()
        instance.put(local_file, remote_tmpfile)
        instance.execute('/usr/bin/sudo /bin/cp -f %s ' \
            '/etc/snmp/snmpd.conf' % remote_tmpfile)
        instance.execute('/usr/bin/sudo /bin/systemctl restart snmpd.service')




