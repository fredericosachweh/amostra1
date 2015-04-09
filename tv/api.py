#!/usr/bin/env python
# -*- encoding:utf8 -*-
from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.authentication import SessionAuthentication

from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource

from tastypie.exceptions import Unauthorized


import logging
log = logging.getLogger('api')


class ChannelResourceAuthorization(Authorization):
    # http://django-tastypie.readthedocs.org/en/latest/authorization.html

    def read_list(self, object_list, bundle):
        user = bundle.request.user
        log.debug('Readlist request to:%s', user)
        if user.is_anonymous():
            raise Unauthorized("Unauthorized")
        return object_list

    def read_detail(self, object_list, bundle):
        return not bundle.request.user.is_anonymous()


class ChannelResource(NamespacedModelResource):
    source = fields.CharField(blank=True)
    next = fields.CharField()
    previous = fields.CharField()

    class Meta:
        Channel = apps.get_model('tv', 'Channel')
        queryset = Channel.objects.filter(
            enabled=True,
            source__isnull=False
        )
        authorization = ChannelResourceAuthorization()
        # authorization = SetTopBoxAuthorization()
        # authorization = Authorization()
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
        SetTopBox = apps.get_model('client', 'SetTopBox')
        Channel = apps.get_model('client', 'Channel')
        user = request.user
        log.debug('ChannelResource User=%s', user)
        if user.is_anonymous():
            log.debug('Return empt list')
            return Channel.objects.none()
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
        SetTopBox = apps.get_model('client', 'SetTopBox')
        Channel = apps.get_model('tv', 'Channel')
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
                obj_list = Channel.objects.all()
        else:
            obj_list = Channel.objects.none()
        return obj_list

    def dehydrate(self, bundle):
        "This method populate previour and next (linked list)"
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
    next = fields.CharField()
    previous = fields.CharField()

    class Meta:
        Channel = apps.get_model('tv', 'Channel')
        queryset = Channel.objects.filter(
            enabled=True,
            source__isnull=False
        )
        authorization = ReadOnlyAuthorization()
        excludes = ['enabled']
        allowed_methods = ['get']
        resource_name = 'channel'
        fields = ['channelid', 'description', 'name', 'number', 'thumb']
        authentication = MultiAuthentication(
            Authentication(),
            ApiKeyAuthentication())

    def dehydrate(self, bundle):
        "This method populate previour and next (linked list)"
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


class MyChannelResourceAuthorization(Authorization):
    # http://django-tastypie.readthedocs.org/en/latest/authorization.html

    def read_list(self, object_list, bundle):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        user = bundle.request.user
        request = bundle.request
        log.debug('Readlist request to:%s', user)
        if user.is_anonymous():
            raise Unauthorized("Unauthorized")
        if request.user.groups.filter(name='settopbox').exists():
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = SetTopBox.objects.get(serial_number=serial)
            channels = stb.get_channels()
            return channels
        return object_list

    def read_detail(self, object_list, bundle):
        return not bundle.request.user.is_anonymous()


class MyChannelResource(NamespacedModelResource):
    source = fields.CharField(blank=True)

    class Meta:
        Channel = apps.get_model('tv', 'Channel')
        queryset = Channel.objects.filter(
            enabled=True,
            source__isnull=False
        )
        # excludes = ['enabled', 'description', 'enabled', 'name']
        fields = ['id', 'channelid', 'number', 'buffer_size']
        allowed_methods = ['get']
        resource_name = 'userchannel'
        authorization = MyChannelResourceAuthorization()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            SessionAuthentication(),
            Authentication(),
            ApiKeyAuthentication())

    def dehydrate_source(self, bundle):
        return '%s:%d' % (bundle.obj.source.ip, bundle.obj.source.port)


api_v1 = NamespacedApi(api_name='v1', urlconf_namespace='tv_v1')
api_v1.register(ChannelResource())

api_v2 = NamespacedApi(api_name='v2', urlconf_namespace='tv_v2')
api_v2.register(AllChannelResource())
api_v2.register(MyChannelResource())

apis = [api_v1, api_v2]
