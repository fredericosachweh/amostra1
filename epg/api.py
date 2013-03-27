#!/usr/bin/env python
# -*- encoding:utf8 -*-

import time
from django.utils import timezone
#from django.conf.urls.defaults import *

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource

import models
import logging


class MetaDefault:
    authorization = Authorization()
    allowed_methods = ['get']


class LangResource(NamespacedModelResource):
    class Meta(MetaDefault):
        queryset = models.Lang.objects.all()


class UrlResource(NamespacedModelResource):
    class Meta(MetaDefault):
        queryset = models.Url.objects.all()


class IconResource(NamespacedModelResource):
    class Meta(MetaDefault):
        queryset = models.Icon.objects.all()


class Display_NameResource(NamespacedModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)

    class Meta(MetaDefault):
        queryset = models.Display_Name.objects.all()


class ChannelResource(NamespacedModelResource):
    display_name = fields.CharField()
    urls = fields.ToManyField(UrlResource, 'urls', full=True, null=True)
    icons = fields.ToManyField(IconResource, 'icons', full=True, null=True)

    class Meta(MetaDefault):
        #XXX: Filtrar apenas canais que sejam relacionados com canais
        queryset = models.Channel.objects.all()
        filtering = {
            "channelid": ALL
        }

    def dehydrate_display_name(self, bundle):
        #XXX: Selecionar o idioma padrão ou proximo válido.
        r = bundle.obj.display_names.all()
        return r[0].value if (len(r) > 0) else None


class TitleResource(NamespacedModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)

    class Meta(MetaDefault):
        queryset = models.Title.objects.all()


class DescriptionResource(NamespacedModelResource):
    #XXX: Corrigir bug: The model '' has an empty attribute 'lang_id' and
    #doesn't allow a null value
    lang = fields.ForeignKey(LangResource, 'lang', null=True)

    class Meta(MetaDefault):
        queryset = models.Description.objects.all()


class StaffResource(NamespacedModelResource):
    class Meta(MetaDefault):
        queryset = models.Staff.objects.all()


class ActorResource(NamespacedModelResource):
    class Meta(MetaDefault):
        queryset = models.Actor.objects.all()


class RatingResource(NamespacedModelResource):
    class Meta(MetaDefault):
        queryset = models.Rating.objects.all()


class LanguageResource(NamespacedModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)

    class Meta(MetaDefault):
        queryset = models.Language.objects.all()


class SubtitleResource(NamespacedModelResource):
    language = fields.ForeignKey(LanguageResource, 'language', null=True)

    class Meta(MetaDefault):
        queryset = models.Subtitle.objects.all()


class Star_RatingResource(NamespacedModelResource):
    icons = fields.ToManyField(IconResource, 'icons', full=True, null=True)

    class Meta(MetaDefault):
        queryset = models.Star_Rating.objects.all()


class CategoryResource(NamespacedModelResource):
    lang = fields.ForeignKey(LangResource, 'lang', null=True)

    class Meta(MetaDefault):
        queryset = models.Category.objects.all()


class ProgrammeResource(NamespacedModelResource):
    title = fields.CharField()
    secondary_title = fields.CharField()
    description = fields.CharField()
    rating = fields.ForeignKey(RatingResource, 'rating', full=False, null=True)
    categories = fields.ToManyField(CategoryResource, 'categories', full=False,
        null=True)
    star_ratings = fields.ToManyField(Star_RatingResource, 'star_ratings',
        full=False, null=True)
    actors = fields.ToManyField(ActorResource, 'actors', full=True, null=True)
    directors = fields.ToManyField(StaffResource, 'directors', full=True,
        null=True)

    class Meta(MetaDefault):
        queryset = models.Programme.objects.all()
        filtering = {
            'video_aspect': ALL,
            'actors': ALL,
            'title': ALL
        }

    def dehydrate_title(self, bundle):
        #XXX: Selecionar o idioma padrão ou proximo válido.
        r = bundle.obj.titles.all()
        return r[0].value if (len(r) > 0) else None

    def dehydrate_secondary_title(self, bundle):
        #XXX: Selecionar o idioma padrão ou proximo válido.
        r = bundle.obj.secondary_titles.all()
        return r[0].value if (len(r) > 0) else None

    def dehydrate_description(self, bundle):
        #XXX: Selecionar o idioma padrão ou proximo válido.
        r = bundle.obj.descriptions.all()
        return r[0].value if (len(r) > 0) else None


class GuideResource(NamespacedModelResource):
    start_timestamp = fields.IntegerField()
    stop_timestamp = fields.IntegerField()
    channel = fields.ToOneField(ChannelResource, 'channel', full=False)
    programme = fields.ToOneField(ProgrammeResource, 'programme', full=True)
    next = fields.ForeignKey('self', 'next', full=False, null=True)
    previous = fields.ForeignKey('self', 'previous', full=False, null=True)

    class Meta(MetaDefault):
        queryset = models.Guide.objects.all().order_by('start')
        filtering = {
            "channel": ALL_WITH_RELATIONS,
            "start": ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            "stop": ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }

    def dehydrate_start_timestamp(self, bundle):
        return time.mktime(bundle.obj.start.timetuple())

    def dehydrate_stop_timestamp(self, bundle):
        return time.mktime(bundle.obj.stop.timetuple())

    def build_filters(self, filters=None):
        #log = logging.getLogger('api')
        newfilter = {}
        if filters is None:
            filters = {}
        for f in filters:
            if f.endswith('_timestamp'):
                k = f[:-10]
                v = filters.get(f)
                try:
                    #log.debug('Filter:%s=%s', k, v)
                    v = timezone.datetime.fromtimestamp(float(v), timezone.utc)
                    #log.debug('time:%s', v)
                except:
                    v = None
                newfilter[k] = str(v)
            else:
                newfilter[f] = filters[f]
        orm_filters = super(GuideResource, self).build_filters(newfilter)
        return orm_filters

api = NamespacedApi(api_name='v1', urlconf_namespace='epg')
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
