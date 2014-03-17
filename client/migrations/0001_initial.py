# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SetTopBox'
        db.create_table(u'client_settopbox', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('serial_number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('mac', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'client', ['SetTopBox'])

        # Adding model 'SetTopBoxParameter'
        db.create_table(u'client_settopboxparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=250, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=250, db_index=True)),
            ('settopbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.SetTopBox'])),
        ))
        db.send_create_signal(u'client', ['SetTopBoxParameter'])

        # Adding unique constraint on 'SetTopBoxParameter', fields ['key', 'value', 'settopbox']
        db.create_unique(u'client_settopboxparameter', ['key', 'value', 'settopbox_id'])

        # Adding model 'SetTopBoxChannel'
        db.create_table(u'client_settopboxchannel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('settopbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.SetTopBox'])),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tv.Channel'])),
            ('recorder', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'client', ['SetTopBoxChannel'])

        # Adding unique constraint on 'SetTopBoxChannel', fields ['settopbox', 'channel']
        db.create_unique(u'client_settopboxchannel', ['settopbox_id', 'channel_id'])

        # Adding model 'SetTopBoxConfig'
        db.create_table(u'client_settopboxconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=250, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=250, db_index=True)),
            ('value_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('settopbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.SetTopBox'])),
        ))
        db.send_create_signal(u'client', ['SetTopBoxConfig'])

        # Adding unique constraint on 'SetTopBoxConfig', fields ['key', 'settopbox']
        db.create_unique(u'client_settopboxconfig', ['key', 'settopbox_id'])

        # Adding model 'SetTopBoxMessage'
        db.create_table(u'client_settopboxmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=250, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('api_reference', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'client', ['SetTopBoxMessage'])


    def backwards(self, orm):
        # Removing unique constraint on 'SetTopBoxConfig', fields ['key', 'settopbox']
        db.delete_unique(u'client_settopboxconfig', ['key', 'settopbox_id'])

        # Removing unique constraint on 'SetTopBoxChannel', fields ['settopbox', 'channel']
        db.delete_unique(u'client_settopboxchannel', ['settopbox_id', 'channel_id'])

        # Removing unique constraint on 'SetTopBoxParameter', fields ['key', 'value', 'settopbox']
        db.delete_unique(u'client_settopboxparameter', ['key', 'value', 'settopbox_id'])

        # Deleting model 'SetTopBox'
        db.delete_table(u'client_settopbox')

        # Deleting model 'SetTopBoxParameter'
        db.delete_table(u'client_settopboxparameter')

        # Deleting model 'SetTopBoxChannel'
        db.delete_table(u'client_settopboxchannel')

        # Deleting model 'SetTopBoxConfig'
        db.delete_table(u'client_settopboxconfig')

        # Deleting model 'SetTopBoxMessage'
        db.delete_table(u'client_settopboxmessage')


    models = {
        u'client.settopbox': {
            'Meta': {'object_name': 'SetTopBox'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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

    complete_apps = ['client']