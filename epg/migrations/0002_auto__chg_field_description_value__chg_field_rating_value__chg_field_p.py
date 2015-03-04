# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Programme', fields ['programid']
        db.delete_unique(u'epg_programme', ['programid'])


        # Changing field 'Description.value'
        db.alter_column(u'epg_description', 'value', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Rating.value'
        db.alter_column(u'epg_rating', u'value', self.gf('django.db.models.fields.CharField')(max_length=100, db_column=u'value'))

        # Changing field 'Programme.programid'
        db.alter_column(u'epg_programme', 'programid', self.gf('django.db.models.fields.CharField')(max_length=32))

    def backwards(self, orm):

        # Changing field 'Description.value'
        db.alter_column(u'epg_description', 'value', self.gf('django.db.models.fields.CharField')(max_length=512, null=True))

        # Changing field 'Rating.value'
        db.alter_column(u'epg_rating', 'value', self.gf('django.db.models.fields.CharField')(max_length=100, db_column='value'))

        # Changing field 'Programme.programid'
        db.alter_column(u'epg_programme', 'programid', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True))
        # Adding unique constraint on 'Programme', fields ['programid']
        db.create_unique(u'epg_programme', ['programid'])


    models = {
        u'epg.actor': {
            'Meta': {'object_name': 'Actor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'role': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'epg.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Lang']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'epg.channel': {
            'Meta': {'object_name': 'Channel'},
            'channelid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '254', 'db_index': 'True'}),
            'display_names': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Display_Name']", 'null': 'True', 'blank': 'True'}),
            'icons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Icon']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'urls': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Url']", 'null': 'True', 'blank': 'True'})
        },
        u'epg.country': {
            'Meta': {'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'epg.description': {
            'Meta': {'object_name': 'Description'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Lang']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'epg.display_name': {
            'Meta': {'object_name': 'Display_Name'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Lang']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'epg.epg_source': {
            'Meta': {'object_name': 'Epg_Source'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'filefield': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModification': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'unique': 'True', 'blank': 'True'}),
            'major_stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'minor_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'numberofElements': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'epg.episode_num': {
            'Meta': {'object_name': 'Episode_Num'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'system': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'epg.guide': {
            'Meta': {'ordering': "(u'start',)", 'object_name': 'Guide'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Channel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'next_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['epg.Guide']"}),
            'previous': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'previous_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['epg.Guide']"}),
            'programme': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Programme']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'stop': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'epg.icon': {
            'Meta': {'object_name': 'Icon'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'src': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'})
        },
        u'epg.lang': {
            'Meta': {'object_name': 'Lang'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'})
        },
        u'epg.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Lang']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'epg.programme': {
            'Meta': {'object_name': 'Programme'},
            'actors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Actor']", 'null': 'True', 'blank': 'True'}),
            'adapters': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'adapter'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'audio_present': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'audio_stereo': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Category']", 'null': 'True', 'blank': 'True'}),
            'commentators': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'commentator'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'composers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'composer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Country']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'descriptions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Description']", 'null': 'True', 'blank': 'True'}),
            'directors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'director'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'editors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'editor'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'episode_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Episode_Num']", 'null': 'True', 'blank': 'True'}),
            'guests': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'guest'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'language'", 'null': 'True', 'to': u"orm['epg.Language']"}),
            'length': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'original_language'", 'null': 'True', 'to': u"orm['epg.Language']"}),
            'presenters': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'presenter'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'producers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'producer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'programid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'rating': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Rating']", 'null': 'True', 'blank': 'True'}),
            'secondary_titles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'secondary_titles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Title']"}),
            'star_ratings': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Star_Rating']", 'null': 'True', 'blank': 'True'}),
            'subtitles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Language']", 'null': 'True', 'blank': 'True'}),
            'titles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'titles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Title']"}),
            'video_aspect': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'video_colour': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'video_present': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'video_quality': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'writers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'writer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"})
        },
        u'epg.rating': {
            'Meta': {'unique_together': "((u'system', u'value'),)", 'object_name': 'Rating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'int_value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'null': 'True'}),
            'system': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "u'value'", 'db_index': 'True'})
        },
        u'epg.staff': {
            'Meta': {'object_name': 'Staff'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'epg.star_rating': {
            'Meta': {'object_name': 'Star_Rating'},
            'icons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Icon']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'system': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'})
        },
        u'epg.subtitle': {
            'Meta': {'object_name': 'Subtitle'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Language']", 'null': 'True', 'blank': 'True'}),
            'subtitle_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'epg.title': {
            'Meta': {'object_name': 'Title'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Lang']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'})
        },
        u'epg.url': {
            'Meta': {'object_name': 'Url'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'epg.xmltv_source': {
            'Meta': {'object_name': 'XMLTV_Source', '_ormbases': [u'epg.Epg_Source']},
            u'epg_source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['epg.Epg_Source']", 'unique': 'True', 'primary_key': 'True'}),
            'generator_info_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'generator_info_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source_data_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source_info_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source_info_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['epg']