# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('tv', '0001_initial'),
        ('client', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding field 'StreamRecorder.channel'
        db.add_column(u'device_streamrecorder', 'channel',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tv.Channel'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'StreamPlayer.stb'
        db.add_column(u'device_streamplayer', 'stb',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.SetTopBox'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'StreamRecorder.channel'
        db.delete_column(u'device_streamrecorder', 'channel_id')

        # Deleting field 'StreamPlayer.stb'
        db.delete_column(u'device_streamplayer', 'stb_id')


    models = {
        u'client.settopbox': {
            'Meta': {'object_name': 'SetTopBox'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'nbridge': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['nbridge.Nbridge']", 'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
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
            'stb': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.SetTopBox']", 'null': 'True', 'blank': 'True'}),
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
        u'nbridge.nbridge': {
            'Meta': {'ordering': "[u'server__name']", 'object_name': 'Nbridge', '_ormbases': [u'device.DeviceServer']},
            'debug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debug_port': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'env_val': ('django.db.models.fields.CharField', [], {'default': "u'production'", 'max_length': '20'}),
            'log_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'middleware_addr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
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
