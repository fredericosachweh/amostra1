# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Server'
        db.create_table(u'device_server', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('host', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('rsakey', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('ssh_port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=22, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('msg', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('offline_mode', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('server_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'device', ['Server'])

        # Adding model 'NIC'
        db.create_table(u'device_nic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Server'])),
            ('ipv4', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal(u'device', ['NIC'])

        # Adding unique constraint on 'NIC', fields ['name', 'server']
        db.create_unique(u'device_nic', ['name', 'server_id'])

        # Adding model 'UniqueIP'
        db.create_table(u'device_uniqueip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, unique=True, null=True)),
            ('port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10000)),
            ('sequential', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=2)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'device', ['UniqueIP'])

        # Adding model 'DeviceServer'
        db.create_table(u'device_deviceserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Server'])),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pid', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal(u'device', ['DeviceServer'])

        # Adding model 'Antenna'
        db.create_table(u'device_antenna', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('satellite', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lnb_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'device', ['Antenna'])

        # Adding model 'DemuxedService'
        db.create_table(u'device_demuxedservice', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('sid', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('provider', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('service_desc', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nic_src', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.NIC'], null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
        ))
        db.send_create_signal(u'device', ['DemuxedService'])

        # Adding model 'DigitalTunerHardware'
        db.create_table(u'device_digitaltunerhardware', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Server'])),
            ('id_vendor', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id_product', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('bus', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('driver', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('uniqueid', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True, null=True)),
            ('adapter_nr', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'device', ['DigitalTunerHardware'])

        # Adding unique constraint on 'DigitalTunerHardware', fields ['server', 'adapter_nr']
        db.create_unique(u'device_digitaltunerhardware', ['server_id', 'adapter_nr'])

        # Adding model 'DvbTuner'
        db.create_table(u'device_dvbtuner', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('frequency', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('symbol_rate', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('modulation', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('polarization', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fec', self.gf('django.db.models.fields.CharField')(default=u'999', max_length=200)),
            ('adapter', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('antenna', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Antenna'])),
        ))
        db.send_create_signal(u'device', ['DvbTuner'])

        # Adding model 'IsdbTuner'
        db.create_table(u'device_isdbtuner', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('frequency', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('modulation', self.gf('django.db.models.fields.CharField')(default=u'qam', max_length=200)),
            ('bandwidth', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=6, null=True)),
            ('adapter', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
        ))
        db.send_create_signal(u'device', ['IsdbTuner'])

        # Adding model 'UnicastInput'
        db.create_table(u'device_unicastinput', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.NIC'])),
            ('port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10000)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default=u'udp', max_length=20)),
        ))
        db.send_create_signal(u'device', ['UnicastInput'])

        # Adding model 'MulticastInput'
        db.create_table(u'device_multicastinput', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.NIC'])),
            ('port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10000)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default=u'udp', max_length=20)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal(u'device', ['MulticastInput'])

        # Adding model 'FileInput'
        db.create_table(u'device_fileinput', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('repeat', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('nic_src', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.NIC'])),
        ))
        db.send_create_signal(u'device', ['FileInput'])

        # Adding model 'MulticastOutput'
        db.create_table(u'device_multicastoutput', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.NIC'])),
            ('port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10000)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default=u'udp', max_length=20)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15)),
            ('nic_sink', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'nic_sink', to=orm['device.NIC'])),
        ))
        db.send_create_signal(u'device', ['MulticastOutput'])

        # Adding model 'Storage'
        db.create_table(u'device_storage', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('folder', self.gf('django.db.models.fields.CharField')(default='/var/lib/iptv/recorder', max_length=500)),
            ('hdd_ssd', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('peso', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('limit_rec_hd', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('limit_rec_sd', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('limit_play_hd', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('limit_play_sd', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('n_recorders', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('n_players', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'device', ['Storage'])

        # Adding model 'StreamRecorder'
        db.create_table(u'device_streamrecorder', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('rotate', self.gf('django.db.models.fields.PositiveIntegerField')(default=60)),
            ('keep_time', self.gf('django.db.models.fields.PositiveIntegerField')(default=48)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tv.Channel'], null=True, blank=True)),
            ('nic_sink', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.NIC'])),
            ('storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Storage'])),
            ('stream_hd', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'device', ['StreamRecorder'])

        # Adding model 'StreamPlayer'
        db.create_table(u'device_streamplayer', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('recorder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.StreamRecorder'])),
            ('stb_ip', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15, db_index=True)),
            ('stb_port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=12000)),
            ('control_socket', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('time_shift', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'device', ['StreamPlayer'])

        # Adding model 'SoftTranscoder'
        db.create_table(u'device_softtranscoder', (
            (u'deviceserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['device.DeviceServer'], unique=True, primary_key=True)),
            ('nic_sink', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'soft_transcoder_nic_sink', to=orm['device.NIC'])),
            ('nic_src', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'soft_transcoder_nic_src', to=orm['device.NIC'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('transcode_audio', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('audio_codec', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('apply_gain', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gain_value', self.gf('django.db.models.fields.FloatField')(default=1.0, null=True, blank=True)),
            ('apply_offset', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('offset_value', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal(u'device', ['SoftTranscoder'])

        # Adding model 'RealTimeEncript'
        db.create_table(u'device_realtimeencript', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'device', ['RealTimeEncript'])


    def backwards(self, orm):
        # Removing unique constraint on 'DigitalTunerHardware', fields ['server', 'adapter_nr']
        db.delete_unique(u'device_digitaltunerhardware', ['server_id', 'adapter_nr'])

        # Removing unique constraint on 'NIC', fields ['name', 'server']
        db.delete_unique(u'device_nic', ['name', 'server_id'])

        # Deleting model 'Server'
        db.delete_table(u'device_server')

        # Deleting model 'NIC'
        db.delete_table(u'device_nic')

        # Deleting model 'UniqueIP'
        db.delete_table(u'device_uniqueip')

        # Deleting model 'DeviceServer'
        db.delete_table(u'device_deviceserver')

        # Deleting model 'Antenna'
        db.delete_table(u'device_antenna')

        # Deleting model 'DemuxedService'
        db.delete_table(u'device_demuxedservice')

        # Deleting model 'DigitalTunerHardware'
        db.delete_table(u'device_digitaltunerhardware')

        # Deleting model 'DvbTuner'
        db.delete_table(u'device_dvbtuner')

        # Deleting model 'IsdbTuner'
        db.delete_table(u'device_isdbtuner')

        # Deleting model 'UnicastInput'
        db.delete_table(u'device_unicastinput')

        # Deleting model 'MulticastInput'
        db.delete_table(u'device_multicastinput')

        # Deleting model 'FileInput'
        db.delete_table(u'device_fileinput')

        # Deleting model 'MulticastOutput'
        db.delete_table(u'device_multicastoutput')

        # Deleting model 'Storage'
        db.delete_table(u'device_storage')

        # Deleting model 'StreamRecorder'
        db.delete_table(u'device_streamrecorder')

        # Deleting model 'StreamPlayer'
        db.delete_table(u'device_streamplayer')

        # Deleting model 'SoftTranscoder'
        db.delete_table(u'device_softtranscoder')

        # Deleting model 'RealTimeEncript'
        db.delete_table(u'device_realtimeencript')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'device.antenna': {
            'Meta': {'object_name': 'Antenna'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lnb_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'satellite': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'device.demuxedservice': {
            'Meta': {'object_name': 'DemuxedService', '_ormbases': [u'device.DeviceServer']},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nic_src': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.NIC']", 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'service_desc': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'device.deviceserver': {
            'Meta': {'object_name': 'DeviceServer'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Server']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'device.digitaltunerhardware': {
            'Meta': {'unique_together': "((u'server', u'adapter_nr'),)", 'object_name': 'DigitalTunerHardware'},
            'adapter_nr': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'bus': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'driver': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_product': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id_vendor': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Server']"}),
            'uniqueid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'})
        },
        u'device.dvbtuner': {
            'Meta': {'object_name': 'DvbTuner'},
            'adapter': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'antenna': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Antenna']"}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'fec': ('django.db.models.fields.CharField', [], {'default': "u'999'", 'max_length': '200'}),
            'frequency': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modulation': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'polarization': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'symbol_rate': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'device.fileinput': {
            'Meta': {'object_name': 'FileInput', '_ormbases': [u'device.DeviceServer']},
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'nic_src': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.NIC']"}),
            'repeat': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'device.isdbtuner': {
            'Meta': {'object_name': 'IsdbTuner'},
            'adapter': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'bandwidth': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '6', 'null': 'True'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'frequency': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modulation': ('django.db.models.fields.CharField', [], {'default': "u'qam'", 'max_length': '200'})
        },
        u'device.multicastinput': {
            'Meta': {'object_name': 'MulticastInput'},
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.NIC']"}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10000'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "u'udp'", 'max_length': '20'})
        },
        u'device.multicastoutput': {
            'Meta': {'ordering': "(u'ip',)", 'object_name': 'MulticastOutput'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.NIC']"}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'nic_sink': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'nic_sink'", 'to': u"orm['device.NIC']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10000'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "u'udp'", 'max_length': '20'})
        },
        u'device.nic': {
            'Meta': {'unique_together': "((u'name', u'server'),)", 'object_name': 'NIC'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Server']"})
        },
        u'device.realtimeencript': {
            'Meta': {'object_name': 'RealTimeEncript'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'device.server': {
            'Meta': {'object_name': 'Server'},
            'host': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'msg': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'offline_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'rsakey': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'server_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ssh_port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '22', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'device.softtranscoder': {
            'Meta': {'object_name': 'SoftTranscoder', '_ormbases': [u'device.DeviceServer']},
            'apply_gain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'apply_offset': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'audio_codec': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'gain_value': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'}),
            'nic_sink': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'soft_transcoder_nic_sink'", 'to': u"orm['device.NIC']"}),
            'nic_src': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'soft_transcoder_nic_src'", 'to': u"orm['device.NIC']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'offset_value': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'transcode_audio': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'device.storage': {
            'Meta': {'object_name': 'Storage', '_ormbases': [u'device.DeviceServer']},
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'folder': ('django.db.models.fields.CharField', [], {'default': "'/var/lib/iptv/recorder'", 'max_length': '500'}),
            'hdd_ssd': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'limit_play_hd': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'limit_play_sd': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'limit_rec_hd': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'limit_rec_sd': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'n_players': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'n_recorders': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'peso': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'})
        },
        u'device.streamplayer': {
            'Meta': {'object_name': 'StreamPlayer', '_ormbases': [u'device.DeviceServer']},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'control_socket': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'recorder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.StreamRecorder']"}),
            'stb_ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15', 'db_index': 'True'}),
            'stb_port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '12000'}),
            'time_shift': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'device.streamrecorder': {
            'Meta': {'object_name': 'StreamRecorder', '_ormbases': [u'device.DeviceServer']},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tv.Channel']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'keep_time': ('django.db.models.fields.PositiveIntegerField', [], {'default': '48'}),
            'nic_sink': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.NIC']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'rotate': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Storage']"}),
            'stream_hd': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'device.unicastinput': {
            'Meta': {'object_name': 'UnicastInput'},
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.NIC']"}),
            'port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10000'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "u'udp'", 'max_length': '20'})
        },
        u'device.uniqueip': {
            'Meta': {'ordering': "(u'ip',)", 'object_name': 'UniqueIP'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'unique': 'True', 'null': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10000'}),
            'sequential': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'})
        },
        u'tv.channel': {
            'Meta': {'ordering': "('number',)", 'object_name': 'Channel'},
            'buffer_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'channelid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.PositiveSmallIntegerField', [], {'unique': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.MulticastOutput']"}),
            'thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['device']