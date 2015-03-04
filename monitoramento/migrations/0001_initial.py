# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MonServer'
        db.create_table(u'monitoramento_monserver', (
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
            ('http_port', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=80, null=True, blank=True)),
            ('http_username', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('http_password', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('server_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'monitoramento', ['MonServer'])


    def backwards(self, orm):
        # Deleting model 'MonServer'
        db.delete_table(u'monitoramento_monserver')


    models = {
        u'monitoramento.monserver': {
            'Meta': {'object_name': 'MonServer'},
            'host': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15', 'blank': 'True'}),
            'http_password': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'http_port': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '80', 'null': 'True', 'blank': 'True'}),
            'http_username': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['monitoramento']