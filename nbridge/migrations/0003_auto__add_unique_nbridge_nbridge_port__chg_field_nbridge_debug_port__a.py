# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Nbridge', fields ['nbridge_port']
        db.create_unique(u'nbridge_nbridge', ['nbridge_port'])


        # Changing field 'Nbridge.debug_port'
        db.alter_column(u'nbridge_nbridge', 'debug_port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(unique=True, null=True))
        # Adding unique constraint on 'Nbridge', fields ['debug_port']
        db.create_unique(u'nbridge_nbridge', ['debug_port'])


    def backwards(self, orm):
        # Removing unique constraint on 'Nbridge', fields ['debug_port']
        db.delete_unique(u'nbridge_nbridge', ['debug_port'])

        # Removing unique constraint on 'Nbridge', fields ['nbridge_port']
        db.delete_unique(u'nbridge_nbridge', ['nbridge_port'])


        # Changing field 'Nbridge.debug_port'
        db.alter_column(u'nbridge_nbridge', 'debug_port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=13000))

    models = {
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
            'debug_port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5858', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'deviceserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['device.DeviceServer']", 'unique': 'True', 'primary_key': 'True'}),
            'env_val': ('django.db.models.fields.CharField', [], {'default': "u'production'", 'max_length': '20'}),
            'log_level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'middleware_addr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nbridge_port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '13000', 'unique': 'True'})
        }
    }

    complete_apps = ['nbridge']