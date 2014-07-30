# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SetTopBox.ip'
        db.add_column(u'client_settopbox', 'ip',
                      self.gf('django.db.models.fields.GenericIPAddressField')(default=None, max_length=39, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SetTopBox.ip'
        db.delete_column(u'client_settopbox', 'ip')


    models = {
        u'client.settopbox': {
            'Meta': {'object_name': 'SetTopBox'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'default': 'None', 'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'nbridge': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['nbridge.Nbridge']", 'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'client.settopboxbehaviorflag': {
            'Meta': {'object_name': 'SetTopBoxBehaviorFlag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'client.settopboxchannel': {
            'Meta': {'ordering': "(u'settopbox', u'channel__number')", 'unique_together': "((u'settopbox', u'channel'),)", 'object_name': 'SetTopBoxChannel'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tv.Channel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recorder': ('django.db.models.fields.BooleanField', [], {}),
            'settopbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.SetTopBox']"})
        },
        u'client.settopboxconfig': {
            'Meta': {'unique_together': "((u'key', u'settopbox'),)", 'object_name': 'SetTopBoxConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'settopbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.SetTopBox']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'client.settopboxmessage': {
            'Meta': {'object_name': 'SetTopBoxMessage'},
            'api_reference': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'client.settopboxparameter': {
            'Meta': {'unique_together': "((u'key', u'value', u'settopbox'),)", 'object_name': 'SetTopBoxParameter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'settopbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.SetTopBox']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'})
        },
        u'client.settopboxprogramschedule': {
            'Meta': {'ordering': "(u'settopbox', u'channel__number')", 'object_name': 'SetTopBoxProgramSchedule'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tv.Channel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'schedule_date': ('django.db.models.fields.BigIntegerField', [], {}),
            'settopbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.SetTopBox']"}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
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
            'Meta': {'ordering': "(u'number',)", 'object_name': 'Channel'},
            'buffer_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'channel_group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['tv.ChannelGroup']", 'null': 'True', 'blank': 'True'}),
            'channelid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.PositiveSmallIntegerField', [], {'unique': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'tv.channelgroup': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'ChannelGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'read_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['client']