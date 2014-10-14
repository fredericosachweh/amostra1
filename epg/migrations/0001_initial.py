# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=512)),
                ('role', models.CharField(db_index=True, max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channelid', models.CharField(unique=True, max_length=254, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Display_Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Epg_Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filefield', models.FileField(upload_to='epg/', verbose_name='Arquivo a ser importado')),
                ('lastModification', models.DateTimeField(auto_now=True, verbose_name='Data da \xfaltima modifica\xe7\xe3o no servidor da revista eletr\xf4nica', unique=True)),
                ('created', models.DateTimeField(auto_now=True, verbose_name='Data de cria\xe7\xe3o')),
                ('numberofElements', models.PositiveIntegerField(default=0, null=True, verbose_name='N\xfamero de elementos neste arquivo', blank=True)),
                ('minor_start', models.DateTimeField(null=True, verbose_name='Menor tempo de inicio encontrado nos programas', blank=True)),
                ('major_stop', models.DateTimeField(null=True, verbose_name='Maior tempo de final encontrado nos programas', blank=True)),
            ],
            options={
                'permissions': (('download_epg', 'Permiss\xe3o para fazer download do EPG'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Episode_Num',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, db_index=True)),
                ('system', models.CharField(max_length=100, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('stop', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('channel', models.ForeignKey(to='epg.Channel')),
                ('next', models.ForeignKey(related_name='next_set', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='epg.Guide', null=True)),
                ('previous', models.ForeignKey(related_name='previous_set', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='epg.Guide', null=True)),
            ],
            options={
                'ordering': ('start',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('src', models.CharField(max_length=10, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=10, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=50, db_index=True)),
                ('lang', models.ForeignKey(blank=True, to='epg.Lang', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('programid', models.CharField(max_length=32, db_index=True)),
                ('date', models.CharField(max_length=50, null=True, blank=True)),
                ('length', models.PositiveIntegerField(null=True, blank=True)),
                ('video_present', models.CharField(max_length=10, null=True, blank=True)),
                ('video_colour', models.CharField(max_length=10, null=True, blank=True)),
                ('video_aspect', models.CharField(max_length=10, null=True, blank=True)),
                ('video_quality', models.CharField(max_length=10, null=True, blank=True)),
                ('audio_present', models.CharField(max_length=10, null=True, blank=True)),
                ('audio_stereo', models.CharField(max_length=10, null=True, blank=True)),
                ('actors', models.ManyToManyField(to='epg.Actor', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('system', models.CharField(max_length=100, db_index=True)),
                ('value', models.CharField(max_length=100, db_column='value', db_index=True)),
                ('int_value', models.PositiveSmallIntegerField(default=0, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=512)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Star_Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=10, db_index=True)),
                ('system', models.CharField(db_index=True, max_length=100, null=True, blank=True)),
                ('icons', models.ManyToManyField(to='epg.Icon', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subtitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtitle_type', models.CharField(max_length=20, null=True, blank=True)),
                ('language', models.ForeignKey(blank=True, to='epg.Language', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=128, db_index=True)),
                ('lang', models.ForeignKey(blank=True, to='epg.Lang', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=200, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='XMLTV_Source',
            fields=[
                ('epg_source_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='epg.Epg_Source')),
                ('source_info_url', models.CharField(max_length=100, null=True, verbose_name='Source info url', blank=True)),
                ('source_info_name', models.CharField(max_length=100, null=True, verbose_name='Source info name', blank=True)),
                ('source_data_url', models.CharField(max_length=100, null=True, verbose_name='Source data url', blank=True)),
                ('generator_info_name', models.CharField(max_length=100, null=True, verbose_name='Generator info name', blank=True)),
                ('generator_info_url', models.CharField(max_length=100, null=True, verbose_name='Generator info url', blank=True)),
            ],
            options={
                'verbose_name': 'Arquivo XML/ZIP EPG',
                'verbose_name_plural': 'Arquivos XML/ZIP EPG',
            },
            bases=('epg.epg_source',),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([('system', 'value')]),
        ),
        migrations.AddField(
            model_name='programme',
            name='adapters',
            field=models.ManyToManyField(related_name='adapter', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='categories',
            field=models.ManyToManyField(to='epg.Category', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='commentators',
            field=models.ManyToManyField(related_name='commentator', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='composers',
            field=models.ManyToManyField(related_name='composer', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='country',
            field=models.ForeignKey(blank=True, to='epg.Country', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='descriptions',
            field=models.ManyToManyField(to='epg.Description', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='directors',
            field=models.ManyToManyField(related_name='director', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='editors',
            field=models.ManyToManyField(related_name='editor', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='episode_numbers',
            field=models.ManyToManyField(to='epg.Episode_Num', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='guests',
            field=models.ManyToManyField(related_name='guest', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='language',
            field=models.ForeignKey(related_name='language', blank=True, to='epg.Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='original_language',
            field=models.ForeignKey(related_name='original_language', blank=True, to='epg.Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='presenters',
            field=models.ManyToManyField(related_name='presenter', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='producers',
            field=models.ManyToManyField(related_name='producer', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='rating',
            field=models.ForeignKey(blank=True, to='epg.Rating', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='secondary_titles',
            field=models.ManyToManyField(related_name='secondary_titles', null=True, to='epg.Title', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='star_ratings',
            field=models.ManyToManyField(to='epg.Star_Rating', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='subtitles',
            field=models.ManyToManyField(to='epg.Language', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='titles',
            field=models.ManyToManyField(related_name='titles', null=True, to='epg.Title', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programme',
            name='writers',
            field=models.ManyToManyField(related_name='writer', null=True, to='epg.Staff', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='guide',
            name='programme',
            field=models.ForeignKey(to='epg.Programme'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='display_name',
            name='lang',
            field=models.ForeignKey(blank=True, to='epg.Lang', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='description',
            name='lang',
            field=models.ForeignKey(blank=True, to='epg.Lang', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='channel',
            name='display_names',
            field=models.ManyToManyField(to='epg.Display_Name', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='channel',
            name='icons',
            field=models.ManyToManyField(to='epg.Icon', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='channel',
            name='urls',
            field=models.ManyToManyField(to='epg.Url', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='lang',
            field=models.ForeignKey(to='epg.Lang'),
            preserve_default=True,
        ),
    ]
