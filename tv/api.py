#!/usr/bin/env python
# -*- encoding:utf8 -*-
from django.conf import settings
from django.conf.urls import url
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.authentication import SessionAuthentication

from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource, ModelResource

from client.models import SetTopBox

import models
import logging


class ChannelResource(NamespacedModelResource):
    source = fields.CharField(blank=True)
    next = fields.CharField()
    previous = fields.CharField()

    class Meta:
        queryset = models.Channel.objects.filter(enabled=True,
            source__isnull=False)
        authorization = ReadOnlyAuthorization()
        #authorization = SetTopBoxAuthorization()
        excludes = ['enabled']
        allowed_methods = ['get']
        urlconf_namespace = 'tv'
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            SessionAuthentication(),
            Authentication(),
            ApiKeyAuthentication())

    def dehydrate_source(self, bundle):
        return '%s:%d' % (bundle.obj.source.ip, bundle.obj.source.port)

    def apply_authorization_limits(self, request, object_list):
        log = logging.getLogger('api')
        user = request.user
        log.debug('ChannelResource User=%s', user)
        if user.is_anonymous():
            log.debug('Return empt list')
            return models.Channel.objects.none()
        object_list = super(ChannelResource, self).apply_authorization_limits(
            request, object_list)
        if user.is_staff:
            return object_list
        if request.user.groups.filter(name='settopbox').exists():
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = SetTopBox.objects.get(serial_number=serial)
            channels = stb.get_channels()
            log.debug('Filter for STB=%s, channels=%s', stb, channels)
            return channels
        return object_list

    def obj_get_list(self, bundle, **kwargs):
        log = logging.getLogger('api')
        user = bundle.request.user
        log.debug('ChannelResource User=%s', user)
        obj_list = super(ChannelResource, self).obj_get_list(bundle, **kwargs)
        if user.is_anonymous() is False:
            if not user.is_staff:
                serial = user.username.replace(settings.STB_USER_PREFIX, '')
                stb = SetTopBox.objects.get(serial_number=serial)
                log.debug('User:%s, SetTopBox:%s', user, stb)
                obj_list = obj_list.filter(
                    settopboxchannel__settopbox=stb,
                    enabled=True,
                    source__isnull=False)
            else:
                obj_list = models.Channel.objects.all()
        else:
            obj_list = models.Channel.objects.none()
        previous = None
        for o in obj_list:
            o.next = None
            if previous is not None:
                previous.next = o
            o.previous = previous
            previous = o
        return obj_list

    def dehydrate(self, bundle):
        u"This method populate previour and next (linked list)"
        if not hasattr(bundle.obj, 'previous'):
            bundle.data['previous'] = None
        else:
            bundle.data['previous'] = self.get_resource_uri(
                bundle.obj.previous)
        if not hasattr(bundle.obj, 'next'):
            bundle.data['next'] = None
        else:
            bundle.data['next'] = self.get_resource_uri(bundle.obj.next)
        return bundle

class AllChannelResource(NamespacedModelResource):
    #source = fields.CharField(blank=True)
    next = fields.CharField()
    previous = fields.CharField()

    class Meta:
        queryset = models.Channel.objects.filter(enabled=False,
            source__isnull=False)
        authorization = ReadOnlyAuthorization()
        #authorization = SetTopBoxAuthorization()
        excludes = ['enabled']
        allowed_methods = ['get']
        #urlconf_namespace = 'tv'
        resource_name = 'channel'
        #api_name = 'v2'
        fields = ['channelid', 'description', 'name', 'number', 'thumb']
        authentication = MultiAuthentication(
            Authentication(),
            ApiKeyAuthentication())

    def dehydrate(self, bundle):
        u"This method populate previour and next (linked list)"
        if not hasattr(bundle.obj, 'previous'):
            bundle.data['previous'] = None
        else:
            bundle.data['previous'] = self.get_resource_uri(
                bundle.obj.previous)
        if not hasattr(bundle.obj, 'next'):
            bundle.data['next'] = None
        else:
            bundle.data['next'] = self.get_resource_uri(bundle.obj.next)
        return bundle

    def obj_get_list(self, bundle, **kwargs):
        obj_list = super(AllChannelResource, self).obj_get_list(bundle, **kwargs)
        previous = None
        for o in obj_list:
            o.next = None
            if previous is not None:
                previous.next = o
            o.previous = previous
            previous = o
        return obj_list

api_v1 = NamespacedApi(api_name='v1', urlconf_namespace='tv_v1')
api_v1.register(ChannelResource())

api_v2 = NamespacedApi(api_name='v2', urlconf_namespace='tv_v2')
api_v2.register(AllChannelResource())

apis = [api_v1, api_v2]
