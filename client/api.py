#!/usr/bin/env python
# -*- encoding:utf8 -*-
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource
from tastypie import fields
from tastypie.constants import ALL
from tastypie.validation import Validation
from tastypie.exceptions import BadRequest
from django.db import IntegrityError
import models
from device import models as devicemodels
from tv.api import ChannelResource
import logging

## Validation:
#http://stackoverflow.com/questions/7435986/how-do-i-configure-tastypie-to-treat-a-field-as-unique

#http://10.1.1.52:8100/tv/api/client/v1/settopboxconfig/8/
#{"key": "app/tv.PARENTAL_CONTROL", "resource_uri": "/tv/api/client/v1/settopboxconfig/8/", "value": "-1", "value_type": "number"}


class MyAuthorization(DjangoAuthorization):

    def is_authorized(self, request, bundle_object=None):
        ok = super(MyAuthorization, self).is_authorized(request, object)
        if ok is False:
            log = logging.getLogger('api')
            log.debug('Method:%s', request.method)
            log.debug('User:%s', request.user)
            log.debug('OK:%s', ok)
        return ok


class SetTopBoxResource(NamespacedModelResource):

    class Meta:
        queryset = models.SetTopBox.objects.all()
        resource_name = 'settopbox'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        authorization = MyAuthorization()
        validation = Validation()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        log = logging.getLogger('api')
        log.debug('New STB=%s', bundle.data.get('serial_number'))
        try:
            bundle = super(SetTopBoxResource, self).obj_create(bundle,
                **kwargs)
        except IntegrityError:
            log.error('Duplicate entry for settopbox.serial_number=%s',
                bundle.data.get('serial_number'))
            raise BadRequest('Duplicate entry for settopbox.serial_number')
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        log = logging.getLogger('api')
        log.debug('Update STB=%s', bundle.data.get('serial_number'))
        try:
            bundle = super(SetTopBoxResource, self).obj_update(bundle,
                request=request, **kwargs)
        except IntegrityError:
            log.error('Duplicate entry for settopbox.serial_number=%s',
                bundle.data.get('serial_number'))
            raise BadRequest('Duplicate entry for settopbox.serial_number')
        return bundle

    #def determine_format(self, request):
    #    return "application/json"


class SetTopBoxParameterResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)

    class Meta:
        queryset = models.SetTopBoxParameter.objects.all()
        resource_name = 'settopboxparameter'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        always_return_data = True
        filtering = {
            "settopbox": ALL,  # ALL_WITH_RELATIONS
            "key": ALL,
            "value": ALL
        }
        validation = Validation()
        authorization = MyAuthorization()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())


class SetTopBoxChannelResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)
    channel = fields.ForeignKey(ChannelResource, 'channel', null=False)

    class Meta:
        queryset = models.SetTopBoxChannel.objects.all()
        resource_name = 'settopboxchannel'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        always_return_data = True
        filtering = {
            "settopbox": ALL,
            "channel": ALL
        }
        validation = Validation()
        authorization = MyAuthorization()
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(SetTopBoxChannelResource, self).obj_create(bundle,
                **kwargs)
        except IntegrityError:
            raise BadRequest('Duplicate entry for settopbox channel')
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        try:
            bundle = super(SetTopBoxChannelResource, self).obj_update(bundle,
                **kwargs)
        except IntegrityError:
            raise BadRequest('Duplicate entry for settopbox channel')
        return bundle


class SetTopBoxAuthorization(Authorization):

    def is_authorized(self, request, bundle_object=None):
        log = logging.getLogger('api')
        if request.user.is_anonymous() is True:
            return False
        user = request.user
        try:
            stb = models.SetTopBox.objects.get(serial_number=user.username)
            log.debug('User:%s, SetTopBox:%s', user, stb)
        except:
            log.error('No STB for user:%s', user)
            return False
        log.debug('Method:%s', request.method)
        log.debug('User:%s', user)
        return True


class SetTopBoxConfigResource(NamespacedModelResource):

    class Meta:
        queryset = models.SetTopBoxConfig.objects.all()
        resource_name = 'settopboxconfig'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        fields = ['key', 'value', 'value_type']
        filtering = {
            "key": ALL,
            "value_type": ALL,
            "settopbox": ALL
        }
        authorization = SetTopBoxAuthorization()
        validation = Validation()
        authentication = Authentication()

    def apply_authorization_limits(self, request, object_list):
        """
        Filtra para o usuário logado.
        """
        log = logging.getLogger('api')
        if request.user.is_anonymous() is False:
            log.debug('user:%s', request.user)
            user = request.user
            stb = models.SetTopBox.objects.get(serial_number=user.username)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            if hasattr(self._meta.authorization, 'apply_limits'):
                object_list = self._meta.authorization.apply_limits(request,
                    object_list)
            object_list = object_list.filter(settopbox=stb)
        else:
            object_list = models.SetTopBoxConfig.objects.get_empty_query_set()
        return object_list

    def obj_create(self, bundle, **kwargs):
        log = logging.getLogger('api')
        log.debug('New Parameter:%s=%s (%s)', bundle.data.get('key'),
            bundle.data.get('value'), bundle.data.get('value_type'))
        if bundle.request.user.is_anonymous() is False:
            user = bundle.request.user
            stb = models.SetTopBox.objects.get(serial_number=user.username)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            try:
                bundle = super(SetTopBoxConfigResource, self).obj_create(
                    bundle, settopbox=stb, **kwargs)
            except IntegrityError:
                log.error('Duplicate entry for settopboxconfig:%s=%s',
                    bundle.data.get('key'), bundle.data.get('value'))
                raise BadRequest('Duplicate entry for settopboxconfig:key=%s' %
                        bundle.data.get('key'))
        else:
            raise BadRequest('')
        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        log = logging.getLogger('api')
        log.debug('Update STB=%s', bundle.data.get('key'))
        try:
            bundle = super(SetTopBoxConfigResource, self).obj_update(bundle,
                **kwargs)
        except IntegrityError:
            log.error('Duplicate entry for settopboxconfig:%s=%s',
                bundle.data.get('key'), bundle.data.get('value'))
            raise BadRequest('Duplicate entry for settopboxconfig')
        return bundle


class StreamRecorderResource(NamespacedModelResource):
    class Meta:
        queryset = devicemodels.StreamRecorder.objects.filter(status=True)

api = NamespacedApi(api_name='v1', urlconf_namespace='client')
api.register(SetTopBoxResource())
api.register(SetTopBoxParameterResource())
api.register(SetTopBoxChannelResource())
api.register(SetTopBoxConfigResource())
