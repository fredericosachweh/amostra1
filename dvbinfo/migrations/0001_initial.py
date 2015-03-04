# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Satellite'
        db.create_table(u'dvbinfo_satellite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('azimuth_degrees', self.gf('django.db.models.fields.FloatField')()),
            ('azimuth_direction', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('logo', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'dvbinfo', ['Satellite'])

        # Adding model 'Transponder'
        db.create_table(u'dvbinfo_transponder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('band', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('frequency', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('symbol_rate', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('polarization', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('fec', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('system', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('modulation', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('logo', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('satellite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dvbinfo.Satellite'])),
        ))
        db.send_create_signal(u'dvbinfo', ['Transponder'])

        # Adding model 'DvbsChannel'
        db.create_table(u'dvbinfo_dvbschannel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('idiom', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('codec', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('crypto', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('last_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('last_update', self.gf('django.db.models.fields.DateField')(null=True)),
            ('logo', self.gf('django.db.models.fields.CharField')(max_length=300, null=True)),
            ('definition', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('transponder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dvbinfo.Transponder'])),
        ))
        db.send_create_signal(u'dvbinfo', ['DvbsChannel'])

        # Adding model 'State'
        db.create_table(u'dvbinfo_state', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'dvbinfo', ['State'])

        # Adding model 'City'
        db.create_table(u'dvbinfo_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dvbinfo.State'])),
        ))
        db.send_create_signal(u'dvbinfo', ['City'])

        # Adding model 'PhysicalChannel'
        db.create_table(u'dvbinfo_physicalchannel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dvbinfo.City'])),
        ))
        db.send_create_signal(u'dvbinfo', ['PhysicalChannel'])

        # Adding model 'VirtualChannel'
        db.create_table(u'dvbinfo_virtualchannel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.FloatField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('epg', self.gf('django.db.models.fields.BooleanField')()),
            ('interactivity', self.gf('django.db.models.fields.BooleanField')()),
            ('physical_channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dvbinfo.PhysicalChannel'])),
        ))
        db.send_create_signal(u'dvbinfo', ['VirtualChannel'])


    def backwards(self, orm):
        # Deleting model 'Satellite'
        db.delete_table(u'dvbinfo_satellite')

        # Deleting model 'Transponder'
        db.delete_table(u'dvbinfo_transponder')

        # Deleting model 'DvbsChannel'
        db.delete_table(u'dvbinfo_dvbschannel')

        # Deleting model 'State'
        db.delete_table(u'dvbinfo_state')

        # Deleting model 'City'
        db.delete_table(u'dvbinfo_city')

        # Deleting model 'PhysicalChannel'
        db.delete_table(u'dvbinfo_physicalchannel')

        # Deleting model 'VirtualChannel'
        db.delete_table(u'dvbinfo_virtualchannel')


    models = {
        u'dvbinfo.city': {
            'Meta': {'object_name': 'City'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dvbinfo.State']"})
        },
        u'dvbinfo.dvbschannel': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DvbsChannel'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'codec': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'crypto': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'definition': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idiom': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'last_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'logo': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'transponder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dvbinfo.Transponder']"})
        },
        u'dvbinfo.physicalchannel': {
            'Meta': {'object_name': 'PhysicalChannel'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dvbinfo.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'dvbinfo.satellite': {
            'Meta': {'ordering': "('azimuth_degrees', 'azimuth_direction')", 'object_name': 'Satellite'},
            'azimuth_degrees': ('django.db.models.fields.FloatField', [], {}),
            'azimuth_direction': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'logo': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dvbinfo.state': {
            'Meta': {'object_name': 'State'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'dvbinfo.transponder': {
            'Meta': {'ordering': "('name', 'frequency')", 'object_name': 'Transponder'},
            'band': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'fec': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'frequency': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'modulation': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'polarization': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'satellite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dvbinfo.Satellite']"}),
            'symbol_rate': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'system': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'})
        },
        u'dvbinfo.virtualchannel': {
            'Meta': {'ordering': "('name',)", 'object_name': 'VirtualChannel'},
            'epg': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interactivity': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.FloatField', [], {}),
            'physical_channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dvbinfo.PhysicalChannel']"})
        }
    }

    complete_apps = ['dvbinfo']