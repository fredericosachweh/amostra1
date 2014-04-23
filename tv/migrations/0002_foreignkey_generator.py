# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('device', '0001_initial'), 
    )

    def forwards(self, orm):
        # Adding field 'Channel.source'
        db.add_column(u'tv_channel', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['device.MulticastOutput']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Channel.source'
        db.delete_column(u'tv_channel', 'source_id')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'device.deviceserver': {
            'Meta': {'object_name': 'DeviceServer'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Server']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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

    complete_apps = ['tv']
