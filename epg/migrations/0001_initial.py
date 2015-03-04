# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Epg_Source'
        db.create_table(u'epg_epg_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filefield', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('lastModification', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, unique=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('numberofElements', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('minor_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('major_stop', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Epg_Source'])

        # Adding model 'XMLTV_Source'
        db.create_table(u'epg_xmltv_source', (
            (u'epg_source_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['epg.Epg_Source'], unique=True, primary_key=True)),
            ('source_info_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('source_info_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('source_data_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('generator_info_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('generator_info_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['XMLTV_Source'])

        # Adding model 'Lang'
        db.create_table(u'epg_lang', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
        ))
        db.send_create_signal(u'epg', ['Lang'])

        # Adding model 'Display_Name'
        db.create_table(u'epg_display_name', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('lang', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Lang'], null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Display_Name'])

        # Adding model 'Icon'
        db.create_table(u'epg_icon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('src', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
        ))
        db.send_create_signal(u'epg', ['Icon'])

        # Adding model 'Url'
        db.create_table(u'epg_url', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'epg', ['Url'])

        # Adding model 'Channel'
        db.create_table(u'epg_channel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channelid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=254, db_index=True)),
        ))
        db.send_create_signal(u'epg', ['Channel'])

        # Adding M2M table for field display_names on 'Channel'
        m2m_table_name = db.shorten_name(u'epg_channel_display_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('channel', models.ForeignKey(orm[u'epg.channel'], null=False)),
            ('display_name', models.ForeignKey(orm[u'epg.display_name'], null=False))
        ))
        db.create_unique(m2m_table_name, ['channel_id', 'display_name_id'])

        # Adding M2M table for field icons on 'Channel'
        m2m_table_name = db.shorten_name(u'epg_channel_icons')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('channel', models.ForeignKey(orm[u'epg.channel'], null=False)),
            ('icon', models.ForeignKey(orm[u'epg.icon'], null=False))
        ))
        db.create_unique(m2m_table_name, ['channel_id', 'icon_id'])

        # Adding M2M table for field urls on 'Channel'
        m2m_table_name = db.shorten_name(u'epg_channel_urls')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('channel', models.ForeignKey(orm[u'epg.channel'], null=False)),
            ('url', models.ForeignKey(orm[u'epg.url'], null=False))
        ))
        db.create_unique(m2m_table_name, ['channel_id', 'url_id'])

        # Adding model 'Title'
        db.create_table(u'epg_title', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('lang', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Lang'], null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Title'])

        # Adding model 'Description'
        db.create_table(u'epg_description', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('lang', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Lang'], null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Description'])

        # Adding model 'Staff'
        db.create_table(u'epg_staff', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal(u'epg', ['Staff'])

        # Adding model 'Actor'
        db.create_table(u'epg_actor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('role', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Actor'])

        # Adding model 'Category'
        db.create_table(u'epg_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('lang', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Lang'])),
        ))
        db.send_create_signal(u'epg', ['Category'])

        # Adding model 'Country'
        db.create_table(u'epg_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'epg', ['Country'])

        # Adding model 'Episode_Num'
        db.create_table(u'epg_episode_num', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('system', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'epg', ['Episode_Num'])

        # Adding model 'Rating'
        db.create_table(u'epg_rating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('system', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, db_column='value', db_index=True)),
            ('int_value', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, null=True)),
        ))
        db.send_create_signal(u'epg', ['Rating'])

        # Adding unique constraint on 'Rating', fields ['system', 'value']
        db.create_unique(u'epg_rating', ['system', 'value'])

        # Adding model 'Language'
        db.create_table(u'epg_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('lang', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Lang'], null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Language'])

        # Adding model 'Subtitle'
        db.create_table(u'epg_subtitle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subtitle_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Language'], null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Subtitle'])

        # Adding model 'Star_Rating'
        db.create_table(u'epg_star_rating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('system', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Star_Rating'])

        # Adding M2M table for field icons on 'Star_Rating'
        m2m_table_name = db.shorten_name(u'epg_star_rating_icons')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('star_rating', models.ForeignKey(orm[u'epg.star_rating'], null=False)),
            ('icon', models.ForeignKey(orm[u'epg.icon'], null=False))
        ))
        db.create_unique(m2m_table_name, ['star_rating_id', 'icon_id'])

        # Adding model 'Programme'
        db.create_table(u'epg_programme', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('programid', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Country'], null=True, blank=True)),
            ('rating', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Rating'], null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='language', null=True, to=orm['epg.Language'])),
            ('original_language', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='original_language', null=True, to=orm['epg.Language'])),
            ('length', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('video_present', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('video_colour', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('video_aspect', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('video_quality', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('audio_present', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('audio_stereo', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'epg', ['Programme'])

        # Adding M2M table for field titles on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_titles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('title', models.ForeignKey(orm[u'epg.title'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'title_id'])

        # Adding M2M table for field secondary_titles on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_secondary_titles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('title', models.ForeignKey(orm[u'epg.title'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'title_id'])

        # Adding M2M table for field descriptions on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_descriptions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('description', models.ForeignKey(orm[u'epg.description'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'description_id'])

        # Adding M2M table for field categories on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('category', models.ForeignKey(orm[u'epg.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'category_id'])

        # Adding M2M table for field episode_numbers on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_episode_numbers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('episode_num', models.ForeignKey(orm[u'epg.episode_num'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'episode_num_id'])

        # Adding M2M table for field subtitles on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_subtitles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('language', models.ForeignKey(orm[u'epg.language'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'language_id'])

        # Adding M2M table for field star_ratings on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_star_ratings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('star_rating', models.ForeignKey(orm[u'epg.star_rating'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'star_rating_id'])

        # Adding M2M table for field actors on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_actors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('actor', models.ForeignKey(orm[u'epg.actor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'actor_id'])

        # Adding M2M table for field directors on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_directors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field writers on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_writers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field adapters on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_adapters')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field producers on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_producers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field composers on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_composers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field editors on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_editors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field presenters on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_presenters')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field commentators on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_commentators')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding M2M table for field guests on 'Programme'
        m2m_table_name = db.shorten_name(u'epg_programme_guests')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('programme', models.ForeignKey(orm[u'epg.programme'], null=False)),
            ('staff', models.ForeignKey(orm[u'epg.staff'], null=False))
        ))
        db.create_unique(m2m_table_name, ['programme_id', 'staff_id'])

        # Adding model 'Guide'
        db.create_table(u'epg_guide', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('programme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Programme'])),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['epg.Channel'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('stop', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('previous', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='previous_set', null=True, on_delete=models.SET_NULL, to=orm['epg.Guide'])),
            ('next', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='next_set', null=True, on_delete=models.SET_NULL, to=orm['epg.Guide'])),
        ))
        db.send_create_signal(u'epg', ['Guide'])


    def backwards(self, orm):
        # Removing unique constraint on 'Rating', fields ['system', 'value']
        db.delete_unique(u'epg_rating', ['system', 'value'])

        # Deleting model 'Epg_Source'
        db.delete_table(u'epg_epg_source')

        # Deleting model 'XMLTV_Source'
        db.delete_table(u'epg_xmltv_source')

        # Deleting model 'Lang'
        db.delete_table(u'epg_lang')

        # Deleting model 'Display_Name'
        db.delete_table(u'epg_display_name')

        # Deleting model 'Icon'
        db.delete_table(u'epg_icon')

        # Deleting model 'Url'
        db.delete_table(u'epg_url')

        # Deleting model 'Channel'
        db.delete_table(u'epg_channel')

        # Removing M2M table for field display_names on 'Channel'
        db.delete_table(db.shorten_name(u'epg_channel_display_names'))

        # Removing M2M table for field icons on 'Channel'
        db.delete_table(db.shorten_name(u'epg_channel_icons'))

        # Removing M2M table for field urls on 'Channel'
        db.delete_table(db.shorten_name(u'epg_channel_urls'))

        # Deleting model 'Title'
        db.delete_table(u'epg_title')

        # Deleting model 'Description'
        db.delete_table(u'epg_description')

        # Deleting model 'Staff'
        db.delete_table(u'epg_staff')

        # Deleting model 'Actor'
        db.delete_table(u'epg_actor')

        # Deleting model 'Category'
        db.delete_table(u'epg_category')

        # Deleting model 'Country'
        db.delete_table(u'epg_country')

        # Deleting model 'Episode_Num'
        db.delete_table(u'epg_episode_num')

        # Deleting model 'Rating'
        db.delete_table(u'epg_rating')

        # Deleting model 'Language'
        db.delete_table(u'epg_language')

        # Deleting model 'Subtitle'
        db.delete_table(u'epg_subtitle')

        # Deleting model 'Star_Rating'
        db.delete_table(u'epg_star_rating')

        # Removing M2M table for field icons on 'Star_Rating'
        db.delete_table(db.shorten_name(u'epg_star_rating_icons'))

        # Deleting model 'Programme'
        db.delete_table(u'epg_programme')

        # Removing M2M table for field titles on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_titles'))

        # Removing M2M table for field secondary_titles on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_secondary_titles'))

        # Removing M2M table for field descriptions on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_descriptions'))

        # Removing M2M table for field categories on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_categories'))

        # Removing M2M table for field episode_numbers on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_episode_numbers'))

        # Removing M2M table for field subtitles on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_subtitles'))

        # Removing M2M table for field star_ratings on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_star_ratings'))

        # Removing M2M table for field actors on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_actors'))

        # Removing M2M table for field directors on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_directors'))

        # Removing M2M table for field writers on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_writers'))

        # Removing M2M table for field adapters on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_adapters'))

        # Removing M2M table for field producers on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_producers'))

        # Removing M2M table for field composers on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_composers'))

        # Removing M2M table for field editors on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_editors'))

        # Removing M2M table for field presenters on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_presenters'))

        # Removing M2M table for field commentators on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_commentators'))

        # Removing M2M table for field guests on 'Programme'
        db.delete_table(db.shorten_name(u'epg_programme_guests'))

        # Deleting model 'Guide'
        db.delete_table(u'epg_guide')


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
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "('start',)", 'object_name': 'Guide'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Channel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['epg.Guide']"}),
            'previous': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'previous_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['epg.Guide']"}),
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
            'adapters': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'adapter'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'audio_present': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'audio_stereo': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Category']", 'null': 'True', 'blank': 'True'}),
            'commentators': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'commentator'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'composers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'composer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Country']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'descriptions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Description']", 'null': 'True', 'blank': 'True'}),
            'directors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'director'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'editors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'editor'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'episode_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Episode_Num']", 'null': 'True', 'blank': 'True'}),
            'guests': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'guest'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'language'", 'null': 'True', 'to': u"orm['epg.Language']"}),
            'length': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'original_language'", 'null': 'True', 'to': u"orm['epg.Language']"}),
            'presenters': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'presenter'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'producers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'producer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"}),
            'programid': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'rating': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['epg.Rating']", 'null': 'True', 'blank': 'True'}),
            'secondary_titles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_titles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Title']"}),
            'star_ratings': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Star_Rating']", 'null': 'True', 'blank': 'True'}),
            'subtitles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['epg.Language']", 'null': 'True', 'blank': 'True'}),
            'titles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'titles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Title']"}),
            'video_aspect': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'video_colour': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'video_present': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'video_quality': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'writers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'writer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['epg.Staff']"})
        },
        u'epg.rating': {
            'Meta': {'unique_together': "(('system', 'value'),)", 'object_name': 'Rating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'int_value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'null': 'True'}),
            'system': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'value'", 'db_index': 'True'})
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