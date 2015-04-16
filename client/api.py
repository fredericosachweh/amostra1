#!/usr/bin/env python
# -*- encoding:utf8 -*-
from __future__ import unicode_literals, absolute_import
import logging
import json
from django.apps import apps
from django.db import IntegrityError
from django.conf import settings
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource
from tastypie import fields
from tastypie.constants import ALL
from tastypie.validation import Validation, FormValidation
from tastypie.serializers import Serializer
from tastypie.exceptions import BadRequest, Unauthorized
from tastypie.models import ApiKey
from device import models as devicemodels
from tv.api import ChannelResource
from . import forms
log = logging.getLogger('api')
erp = logging.getLogger('erp')

# Validation:
# http://stackoverflow.com/questions/7435986/how-do-i-configure-tastypie-to-
# treat-a-field-as-unique

# http://10.1.1.52:8100/tv/api/client/v1/settopboxconfig/8/
# {"key": "app/tv.PARENTAL_CONTROL",
#    "resource_uri": "/tv/api/client/v1/settopboxconfig/8/", "value": "-1",
#    "value_type": "number"}


class MyAuthorization(DjangoAuthorization):

    def is_authorized(self, request, bundle_object=None, *args, **kwargs):
        log.debug('On is_authorized')
        ok = super(MyAuthorization, self).is_authorized(
            request, bundle_object=bundle_object, *args, **kwargs
        )
        if ok is False:
            log.debug('Method:%s', request.method)
            log.debug('User:%s', request.user)
            log.debug('OK:%s', ok)
        return ok


class SetTopBoxValidation(FormValidation):

    def is_valid(self, bundle, request=None, *args, **kwargs):
        if not bundle.data:
            return {'__all__': 'Missing data'}
        return super(SetTopBoxValidation, self).is_valid(
                bundle, request=request,  *args, **kwargs
            )



class SetTopBoxResource(NamespacedModelResource):

    # mac = fields.CharField(u'mac', unique=True, help_text=u'Endereço MAC')
    # serial_number = fields.CharField(u'serial_number', unique=True,
    #     help_text=u'Número serial no equipamento')

    class Meta(object):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        queryset = SetTopBox.objects.all()
        resource_name = 'settopbox'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        fields = ['serial_number', 'mac']
        urlconf_namespace = 'client'
        authorization = MyAuthorization()
        validation = SetTopBoxValidation(form_class=forms.SetTopBoxForm)
        always_return_data = True
        filtering = {
            'mac': ALL,
            'serial_number': ALL
        }
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        from django.db import transaction
        erp.info('New STB=%s', bundle.data.get('serial_number'))
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxResource, self).obj_create(
                    bundle, **kwargs
                )
            except IntegrityError as e:
                erp.error('Error:%s', e)
                transaction.rollback()
                raise BadRequest(e)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        from django.db import transaction
        erp.debug('Update STB=%s', bundle.data.get('serial_number'))
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxResource, self).obj_update(
                    bundle, request=request, **kwargs
                )
            except IntegrityError as e:
                erp.error('Error:%s', e)
                transaction.rollback()
                raise BadRequest(e)
        return bundle


class SetTopBoxParameterResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)

    class Meta(object):
        SetTopBoxParameter = apps.get_model('client', 'SetTopBoxParameter')
        queryset = SetTopBoxParameter.objects.all()
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
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
        queryset = SetTopBoxChannel.objects.all()
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
        from django.db import transaction
        # log.debug('On obj_create(%s,%s,%s)', bundle, request, kwargs)
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxChannelResource, self).obj_create(
                    bundle, **kwargs)
            except IntegrityError as e:
                erp.error('%s', e)
                raise BadRequest(e)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxChannelResource, self).obj_update(
                    bundle, **kwargs
                )
            except IntegrityError as e:
                erp.error('%s', e)
                raise BadRequest(e)
        return bundle


class SetTopBoxSerializer(Serializer):
    """
    Gives message when loading JSON fails.
    """
    def from_json(self, content):
        """
        Override method of `Serializer.from_json`.
        Adds exception message when loading JSON fails.
        """
        try:
            return json.loads(content)
        except ValueError as e:
            errors = {
                "errorCode": "500",
                "errorDescription":
                    "Incorrect JSON format: Reason: \"{}\"".format(e)
            }
            raise BadRequest(errors)


class ProgramScheduleValidation(Validation):

    def is_valid(self, bundle, request=None):
        SetTopBoxProgramSchedule = apps.get_model('client', 'SetTopBoxProgramSchedule')
        if not bundle.data:
            return {
                '__all__':
                    'Missing data, please include channel, url, schedule_date and message.'}

        errors = {}
        schedule_date = bundle.data.get('schedule_date', None)
        url = bundle.data.get('url', None)
        message = bundle.data.get('message', None)
        channel = bundle.data.get('channel', None)

        request_method = bundle.request.META['REQUEST_METHOD']

        if request_method in ('PATCH', 'PUT'):
            bundle_uri = bundle.request.path_info
            try:
                uri_id = bundle_uri.split('/')
                ps = SetTopBoxProgramSchedule.objects.filter(
                    id=uri_id[-2]
                )
                if not ps:
                    errors['errorCode'] = '404'
                    errors['errorDescription'] =\
                        'There is no register on server.'
            except:
                errors['errorCode'] = '404'
                errors['errorDescription'] = 'There is no register on server.'

        if request_method == 'POST':
            if channel is None:
                errors['errorCode'] = '400'
                errors['errorDescription'] = 'There is no channel data.'
            if schedule_date is None:
                errors['errorCode'] = '400'
                errors['errorDescription'] = 'There is no schedule_date data.'
            if url is None:
                errors['errorCode'] = '400'
                errors['errorDescription'] = 'There is no url data.'
            if message is None:
                errors['errorCode'] = '400'
                errors['errorDescription'] = 'There is no message data.'

        return errors


class SetTopBoxAuthorization(Authorization):

    def is_authorized(self, request, bundle_object=None):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        log.debug('bundle_object=%s', bundle_object)
        if request.user.is_anonymous() is True:
            return False
        user = request.user
        serial = user.username.replace(settings.STB_USER_PREFIX, '')
        try:
            stb = SetTopBox.objects.get(serial_number=serial)
            log.debug('User:%s, SetTopBox:%s', user, stb)
        except:
            log.error('No STB for user:%s', user)
            return False
        log.debug('Method:%s', request.method)
        log.debug('User:%s', user)
        return True


class SetTopBoxAuth(Authorization):

    def is_authorized(self, object_list, bundle):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxProgramSchedule = apps.get_model('client', 'SetTopBoxProgramSchedule')
        if bundle.request.user.is_anonymous() is True:
            return False
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')

        try:
            stb = SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('There`s no stb for this serial number: %s', serial)
            return False

        bundle_uri = bundle.request.path_info

        try:
            uri_id = bundle_uri.split('/')
            ps = SetTopBoxProgramSchedule.objects.filter(
                id=uri_id[-2], settopbox_id=stb.id
            )
            if ps:
                return True
            if uri_id[-2] == 'schema':
                return True
        except:
            log.error('There`s no schedule for this uri_id: %s', uri_id)
            return False

    def is_create_authorized(self, object_list, bundle):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        Channel = apps.get_model('tv', 'Channel')
        if bundle.request.user.is_anonymous() is True:
            return False
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')

        channel = bundle.data.get('channel')
        log.debug('There`s no channel for this number: %s', channel)

        try:
            SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('There`s no stb for this serial number: %s', serial)
            return False

        try:
            Channel.objects.get(number=channel)
        except:
            log.error('There`s no channel for this number: %s', channel)
            return False

        return True

    def filter_read_list(self, object_list, bundle):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        if bundle.request.user.is_anonymous() is True:
            raise Unauthorized("Unauthorized")
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')
        try:
            stb = SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('No STB for user:%s', user)
            raise Unauthorized("Unauthorized")
        return object_list.filter(settopbox=stb)

    def read_list(self, object_list, bundle):
        return self.filter_read_list(object_list, bundle)

    def read_detail(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)

    def create_detail(self, object_list, bundle):
        return self.is_create_authorized(object_list, bundle)

    def update_list(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)

    def delete_list(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)


class ProgramScheduleAuthorization(SetTopBoxAuth):

    def is_create_authorized(self, object_list, bundle):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxChannel = apps.get_model('client', 'SetTopBoxChannel')
        Channel = apps.get_model('tv', 'Channel')
        if bundle.request.user.is_anonymous() is True:
            return False
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')
        channel = bundle.data.get('channel')

        try:
            stb = SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('There`s no stb for this serial number: %s', serial)
            return False

        try:
            ch = Channel.objects.get(number=channel)
        except:
            log.error('There`s no channel for this number: %s', channel)
            return False

        try:
            SetTopBoxChannel.objects.filter(
                channel_id=ch.id, settopbox_id=stb.id
            )
        except:
            log.error(
                'There`s no association between channel: %s and settopbox: %s',
                channel, serial
            )
            return False

        setattr(bundle.obj, 'settopbox', stb)
        setattr(bundle.obj, 'channel', ch)

        return True


class SetTopBoxConfigResource(NamespacedModelResource):

    class Meta:
        SetTopBoxConfig = apps.get_model('client', 'SetTopBoxConfig')
        queryset = SetTopBoxConfig.objects.all()
        resource_name = 'settopboxconfig'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        fields = ['key', 'value', 'value_type']
        max_limit = 5000
        limit = 2000
        always_return_data = True
        filtering = {
            "key": ALL,
            "value_type": ALL,
            "settopbox": ALL
        }
        authorization = SetTopBoxAuthorization()
        validation = Validation()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(),
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            )

    def apply_authorization_limits(self, request, object_list):
        """
        Filtra para o usuário logado.
        """
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxConfig = apps.get_model('client', 'SetTopBoxConfig')
        log.debug('User=%s', request.user)
        if request.user.is_anonymous() is False:
            log.debug('user:%s', request.user)
            user = request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = SetTopBox.objects.get(serial_number=serial)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            if hasattr(self._meta.authorization, 'apply_limits'):
                object_list = self._meta.authorization.apply_limits(
                    request, object_list
                )
            object_list = object_list.filter(settopbox=stb)
        else:
            object_list = SetTopBoxConfig.objects.none()
        return object_list

    def obj_create(self, bundle, **kwargs):
        from django.db import transaction
        SetTopBox = apps.get_model('client', 'SetTopBox')
        log.debug(
            'New Parameter:%s=%s (%s)', bundle.data.get('key'),
            bundle.data.get('value'), bundle.data.get('value_type')
        )
        if bundle.request.user.is_anonymous() is False:
            user = bundle.request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = SetTopBox.objects.get(serial_number=serial)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            with transaction.atomic():
                try:
                    bundle = super(SetTopBoxConfigResource, self).obj_create(
                        bundle, settopbox=stb, **kwargs)
                except IntegrityError as e:
                    # log.error('%s', e)
                    raise BadRequest(e)
                return bundle
        else:
            raise BadRequest('')
        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        from django.db import transaction
        SetTopBox = apps.get_model('client', 'SetTopBox')
        log.debug(
            'Update key:%s=%s (%s)', bundle.data.get('key'),
            bundle.data.get('value'), bundle.data.get('value_type')
        )
        if bundle.request.user.is_anonymous() is False:
            user = bundle.request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = SetTopBox.objects.get(serial_number=serial)
            self._meta.queryset.filter(settopbox=stb)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            # TODO: Não deixar um STB moduficar as configs de outro STB
            # if bundle.obj.settopbox_id != stb.id:
            #     raise BadRequest('')
        with transaction.atomic():
            try:
                # print(dir(bundle.obj))
                bundle = super(SetTopBoxConfigResource, self).obj_update(
                    bundle, **kwargs
                )
            except IntegrityError as e:
                log.error('%s', e)
                raise BadRequest(e)
        return bundle

    def obj_get_list(self, bundle, **kwargs):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxConfig = apps.get_model('client', 'SetTopBoxConfig')
        user = bundle.request.user
        log.debug('User=%s', user)
        if user.is_anonymous() is False:
            if not user.is_staff:
                serial = user.username.replace(settings.STB_USER_PREFIX, '')
                log.debug('Serial=%s', serial)
                stb = SetTopBox.objects.get(serial_number=serial)
                log.debug('User:%s, SetTopBox:%s', user, stb)
                # self._meta.queryset.filter(settopbox=stb)
                obj_list = super(SetTopBoxConfigResource, self).obj_get_list(
                    bundle, **kwargs).filter(settopbox=stb)
        else:
            obj_list = SetTopBoxConfig.objects.none()
        return obj_list

    def obj_get(self, bundle, **kwargs):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        SetTopBoxConfig = apps.get_model('client', 'SetTopBoxConfig')
        user = bundle.request.user
        log.debug('User=%s', user)
        obj_list = SetTopBoxConfig.objects.none()
        if user.is_anonymous() is False:
            if not user.is_staff:
                serial = user.username.replace(settings.STB_USER_PREFIX, '')
                log.debug('Serial=%s', serial)
                stb = SetTopBox.objects.get(serial_number=serial)
                log.debug('User:%s, SetTopBox:%s', user, stb)
                obj_list = super(SetTopBoxConfigResource, self).obj_get(
                    bundle, **kwargs)
                if obj_list.settopbox == stb:
                    return obj_list
                else:
                    # raise Unauthorized('')
                    obj_list = SetTopBoxConfig.objects.none()
        else:
            obj_list = SetTopBoxConfig.objects.none()
        return obj_list


class StreamRecorderResource(NamespacedModelResource):
    class Meta:
        queryset = devicemodels.StreamRecorder.objects.filter(status=True)


class APIKeyAuthorization(Authorization):
    # http://django-tastypie.readthedocs.org/en/latest/authorization.html

    def read_list(self, object_list, bundle):
        SetTopBox = apps.get_model('client', 'SetTopBox')
        user = bundle.request.user
        log.debug('Readlist request to:%s', user)
        if user.is_anonymous():
            raise Unauthorized("Unauthorized")
        stb = SetTopBox.get_stb_from_user(bundle.request.user)
        if stb is not None:
            log.debug('STB[online]=%s', stb)
            stb.online = True
            stb.save()
        if user.is_superuser:
            return object_list
        return object_list.filter(user=user)

    def read_detail(self, object_list, bundle):
        return not bundle.request.user.is_anonymous()


class APIKeyResource(NamespacedModelResource):
    class Meta:
        queryset = ApiKey.objects.all()
        authorization = APIKeyAuthorization()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(),
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            )
        filtering = {
            "key": ALL
        }


class SetTopBoxMessage(NamespacedModelResource):
    class Meta:
        SetTopBoxMessage = apps.get_model('client', 'SetTopBoxMessage')
        queryset = SetTopBoxMessage.objects.all()


class SetTopBoxProgramScheduleResource(NamespacedModelResource):

    class Meta:
        SetTopBoxProgramSchedule = apps.get_model('client', 'SetTopBoxProgramSchedule')
        queryset = SetTopBoxProgramSchedule.objects.all()
        resource_name = 'settopboxprogramschedule'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        fields = ['schedule_date', 'message', 'url']
        always_return_data = True
        filtering = {
            "schedule_date": ALL,
            "message": ALL,
            "url": ALL,
        }
        authorization = ProgramScheduleAuthorization()
        validation = ProgramScheduleValidation()
        serializer = SetTopBoxSerializer(formats=['json'])
        authentication = MultiAuthentication(
            ApiKeyAuthentication(),
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            )


class SetTopBoxBehaviorFlagResource(NamespacedModelResource):

    class Meta:
        SetTopBoxBehaviorFlag = apps.get_model('client', 'SetTopBoxBehaviorFlag')
        queryset = SetTopBoxBehaviorFlag.objects.all()


api = NamespacedApi(api_name='v1', urlconf_namespace='client_v1')
api.register(SetTopBoxResource())
api.register(SetTopBoxParameterResource())
api.register(SetTopBoxChannelResource())
api.register(SetTopBoxConfigResource())
api.register(APIKeyResource())
api.register(SetTopBoxMessage())
api.register(SetTopBoxProgramScheduleResource())
api.register(SetTopBoxBehaviorFlagResource())

apis = [api]
