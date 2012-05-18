#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *
from datetime import datetime
import time

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from models import *

class MetaDefault:
    authorization = Authorization()
    allowed_methods = ['get']
    

class LangResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Lang.objects.all()





class UrlResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Url.objects.all()

class IconResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Icon.objects.all()

class Display_NameResource(ModelResource):
    lang = fields.ForeignKey(LangResource, 'lang')
    class Meta(MetaDefault):
        queryset = Display_Name.objects.all()

class ChannelResource(ModelResource):
    display_names = fields.ToManyField(Display_NameResource, 'display_names', full=True)
    icons = fields.ToManyField(IconResource, 'icons', full=True)
    urls = fields.ToManyField(UrlResource, 'urls', full=True)
    class Meta(MetaDefault):
        #XXX: Filtrar apenas canais que sejam relacionados com canais da operadora
        queryset = Channel.objects.all()
        filtering = {
            "channelid": ALL
        }

class TitleResource(ModelResource):
    lang = fields.ForeignKey(LangResource, 'lang')
    class Meta(MetaDefault):
        queryset = Title.objects.all()
        
class DescriptionResource(ModelResource):
    #XXX: Corrigir bug: The model '' has an empty attribute 'lang_id' and doesn't allow a null value
    #lang = fields.ForeignKey(LangResource, 'lang')
    class Meta(MetaDefault):
        queryset = Description.objects.all()

class RatingResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Rating.objects.all()
        
class CategoryResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Category.objects.all()

class ProgrammeResource(ModelResource):
    titles = fields.ToManyField(TitleResource, 'titles', full=True)
    secondary_titles = fields.ToManyField(TitleResource, 'secondary_titles', full=True)
    descriptions = fields.ToManyField(DescriptionResource, 'descriptions', full=True)
    rating = fields.ForeignKey(RatingResource, 'rating', full=False)
    categories = fields.ToManyField(CategoryResource, 'categories', full=False)
    class Meta(MetaDefault):
        queryset = Programme.objects.all()
        filtering = {
            "video_aspect": ALL
        }

class GuideResource(ModelResource):
    start_timestamp = fields.IntegerField()
    stop_timestamp = fields.IntegerField()
    channel = fields.ToOneField(ChannelResource, 'channel', full=False)
    programme = fields.ToOneField(ProgrammeResource, 'programme', full=True)
    current = fields.BooleanField(default=False)
    class Meta(MetaDefault):
        queryset = Guide.objects.all()
        filtering = {
            "channel": ALL_WITH_RELATIONS,
            "start": ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            "stop": ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
    def dehydrate_start_timestamp(self, bundle):
        return '%d'%(time.mktime(bundle.obj.start.timetuple()))
    def dehydrate_stop_timestamp(self, bundle):
        return '%d'%(time.mktime(bundle.obj.stop.timetuple()))
    def dehydrate_current(self, bundle):
        return datetime.now() >= bundle.obj.start and datetime.now() <= bundle.obj.stop

api = Api(api_name='epg')
api.register(ChannelResource())
api.register(LangResource())
api.register(IconResource())
api.register(Display_NameResource())

api.register(DescriptionResource())
api.register(TitleResource())
api.register(RatingResource())
api.register(CategoryResource())
api.register(ProgrammeResource())
api.register(GuideResource())