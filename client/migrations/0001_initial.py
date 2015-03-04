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
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('online', self.gf('django.db.models.fields.BooleanField')(default=False)),
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
            ('recorder', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'client', ['SetTopBoxChannel'])

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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'client.settopboxchannel': {
            'Meta': {'ordering': "(u'settopbox', u'channel__number')", 'object_name': 'SetTopBoxChannel'},
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
        }
    }

    complete_apps = ['client']