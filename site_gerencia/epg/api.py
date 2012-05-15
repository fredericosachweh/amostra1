#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django.conf.urls.defaults import *

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
    lang = fields.ForeignKey(LangResource, 'lang', null=True)
    class Meta(MetaDefault):
        queryset = Display_Name.objects.all()

class ChannelResource(ModelResource):
    display_names = fields.ToManyField(Display_NameResource, 'display_names', full=True, null=True)
    icons = fields.ToManyField(IconResource, 'icons', full=True)
    urls = fields.ToManyField(UrlResource, 'urls', full=True, null=True)
    icons = fields.ToManyField(IconResource, 'icons', full=True, null=True)
    class Meta(MetaDefault):
        #XXX: Filtrar apenas canais que sejam relacionados com canais da operadora
        queryset = Channel.objects.all()
        filtering = {
            "channelid": ALL
        }

class TitleResource(ModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)
    class Meta(MetaDefault):
        queryset = Title.objects.all()
        
class DescriptionResource(ModelResource):
    #XXX: Corrigir bug: The model '' has an empty attribute 'lang_id' and doesn't allow a null value
    lang = fields.ForeignKey(LangResource, 'lang', null=True)
    class Meta(MetaDefault):
        queryset = Description.objects.all()


class StaffResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Staff.objects.all()


class ActorResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Actor.objects.all()


class RatingResource(ModelResource):
    class Meta(MetaDefault):
        queryset = Rating.objects.all()


class LanguageResource(ModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)
    class Meta(MetaDefault):
        queryset = Language.objects.all()


class SubtitleResource(ModelResource):
    language = fields.ForeignKey(LanguageResource, 'language', null=True)
    class Meta(MetaDefault):
        queryset = Subtitle.objects.all()


class Star_RatingResource(ModelResource):
    icons = fields.ToManyField(IconResource, 'icons', full=True, null=True)
    class Meta(MetaDefault):
        queryset = Star_Rating.objects.all()


class CategoryResource(ModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)
    class Meta(MetaDefault):
        queryset = Category.objects.all()

class ProgrammeResource(ModelResource):
    titles = fields.ToManyField(TitleResource, 'titles', full=True, null=True)
    secondary_titles = fields.ToManyField(TitleResource, 'secondary_titles', full=True, null=True)
    descriptions = fields.ToManyField(DescriptionResource, 'descriptions', full=True, null=True)
    rating = fields.ForeignKey(RatingResource, 'rating', full=False, null=True)
    categories = fields.ToManyField(CategoryResource, 'categories', full=False, null=True)
    star_ratings = fields.ToManyField(Star_RatingResource, 'star_ratings', full=False, null=True)
    actors = fields.ToManyField(ActorResource, 'actors', full=False, null=True)
    directors = fields.ToManyField(StaffResource, 'directors', full=False, null=True)
    class Meta(MetaDefault):
        queryset = Programme.objects.all()
        filtering = {
            "video_aspect": ALL
        }

class GuideResource(ModelResource):
    channel = fields.ToOneField(ChannelResource, 'channel', full=False)
    programme = fields.ToOneField(ProgrammeResource, 'programme', full=True)
    class Meta(MetaDefault):
        queryset = Guide.objects.all()
        filtering = {
            "channel": ALL_WITH_RELATIONS,
            "start": ALL,
            "stop": ALL,
        }

api = Api(api_name='epg')
api.register(ChannelResource())
api.register(LangResource())
api.register(IconResource())
api.register(Display_NameResource())
api.register(UrlResource())
api.register(LanguageResource())
api.register(SubtitleResource())
api.register(Star_RatingResource())

api.register(DescriptionResource())
api.register(TitleResource())
api.register(RatingResource())
api.register(CategoryResource())
api.register(ProgrammeResource())
api.register(GuideResource())
api.register(ActorResource())
api.register(StaffResource())