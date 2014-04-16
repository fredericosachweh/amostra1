#!/usr/bin/env python
# -*- encoding:utf8 -*-
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.authentication import SessionAuthentication
from tastypie.api import NamespacedApi
from tastypie.resources import NamespacedModelResource
from tastypie import fields
from tastypie.constants import ALL
from tastypie.validation import Validation
from tastypie.exceptions import BadRequest, NotFound, Unauthorized
from tastypie.models import ApiKey
from django.db import IntegrityError
from django.conf import settings
import models
from device import models as devicemodels
from tv.api import ChannelResource
import logging
log = logging.getLogger('api')
import pdb
## Validation:
#http://stackoverflow.com/questions/7435986/how-do-i-configure-tastypie-to-
#treat-a-field-as-unique

#http://10.1.1.52:8100/tv/api/client/v1/settopboxconfig/8/
#{"key": "app/tv.PARENTAL_CONTROL",
#    "resource_uri": "/tv/api/client/v1/settopboxconfig/8/", "value": "-1",
#    "value_type": "number"}


class MyAuthorization(DjangoAuthorization):

    def is_authorized(self, request, bundle_object=None):
        log.debug('On is_authorized')
        ok = super(MyAuthorization, self).is_authorized(request, object)
        if ok is False:
            log.debug('Method:%s', request.method)
            log.debug('User:%s', request.user)
            log.debug('OK:%s', ok)
        return ok


class SetTopBoxResource(NamespacedModelResource):

    #mac = fields.CharField(u'mac', unique=True, help_text=u'Endereço MAC')
    #serial_number = fields.CharField(u'serial_number', unique=True,
    #     help_text=u'Número serial no equipamento')

    class Meta:
        queryset = models.SetTopBox.objects.all()
        resource_name = 'settopbox'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        fields = ['serial_number', 'mac']
        urlconf_namespace = 'client'
        authorization = MyAuthorization()
        validation = Validation()
        always_return_data = False
        authentication = MultiAuthentication(
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            ApiKeyAuthentication())

    def obj_create(self, bundle, request=None, **kwargs):
        from django.db import transaction
        log.debug('New STB=%s', bundle.data.get('serial_number'))
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxResource, self).obj_create(bundle,
                    **kwargs)
            except IntegrityError, e:
                log.error('%s', e)
                transaction.rollback()
                raise BadRequest(e)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        from django.db import transaction
        log.debug('Update STB=%s', bundle.data.get('serial_number'))
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxResource, self).obj_update(bundle,
                    request=request, **kwargs)
            except IntegrityError, e:
                log.error('%s', e)
                transaction.rollback()
                raise BadRequest(e)
        return bundle


class SetTopBoxParameterResource(NamespacedModelResource):

    settopbox = fields.ForeignKey(SetTopBoxResource, 'settopbox', null=False)

    class Meta:
        queryset = models.SetTopBoxParameter.objects.all()
        resource_name = 'settopboxparameter'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        always_return_data = False
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
        always_return_data = False
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
        #log.debug('On obj_create(%s,%s,%s)', bundle, request, kwargs)
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxChannelResource, self).obj_create(bundle,
                    **kwargs)
            except IntegrityError, e:
                log.error('%s', e)
                raise BadRequest(e)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            try:
                bundle = super(SetTopBoxChannelResource, self).obj_update(bundle,
                    **kwargs)
            except IntegrityError, e:
                log.error('%s', e)
                raise BadRequest(e)
        return bundle


class SetTopBoxAuthorization(Authorization):

    def is_authorized(self, request, bundle_object=None):
        log.debug('bundle_object=%s', bundle_object)
        if request.user.is_anonymous() is True:
            return False
        user = request.user
        serial = user.username.replace(settings.STB_USER_PREFIX, '')
        try:
            stb = models.SetTopBox.objects.get(serial_number=serial)
            log.debug('User:%s, SetTopBox:%s', user, stb)
        except:
            log.error('No STB for user:%s', user)
            return False
        log.debug('Method:%s', request.method)
        log.debug('User:%s', user)
        return True

class SetTopBoxApiAuth(Authorization):
    
    def is_authorized(self, object_list, bundle):
        if bundle.request.user.is_anonymous() is True:
            return False
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')
        
        try:
            stb = models.SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('There`s no stb for this serial number: %s', serial)
            raise Unauthorized("There`s no stb for this serial number")
        
        bundle_uri = bundle.request.path_info
            
        try:
            uri_id = bundle_uri.split('/')
            ps = models.SetTopBoxProgramSchedule.objects.filter(id = uri_id[-2], settopbox_id = stb.id)
            if ps:
                return True
        except:
            if uri_id[-2] == 'schema':
                return True
            log.error('There`s no schedule for this uri_id: %s', uri_id)
            return False
   
    def is_create_authorized(self, object_list, bundle):
        if bundle.request.user.is_anonymous() is True:
            return False
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')
        
        channel = bundle.data.get('channel')
         
        try:
            self.stb = models.SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('There`s no stb for this serial number: %s', serial)
            raise Unauthorized("There`s no stb for this serial number")

        try:
            self.ch = models.Channel.objects.get(number=channel)
        except:
            log.error('There`s no channel for this number: %s', channel)
            raise Unauthorized("There`s no channel for this number")

        try:
            self.stb_ch = models.SetTopBoxChannel.objects.filter(channel_id = self.ch.id, settopbox_id = self.stb.id) 
        except:
            log.error('There`s no association between channel: %s and settopbox: %s',channel, serial)
            raise Unauthorized("There`s no association between channel and serial")
        
        #self.create_object(bundle, self.stb, self.ch)
        return True
    
#    def create_object(self, bundle, stb, ch, **kwargs):
#        pdb.set_trace()
        
#        res = SetTopBoxProgramScheduleResource()
#        request_bundle = res.build_bundle(request=bundle.request)
#        request_bundle.obj.channel = ch 
#        request_bundle.obj.settopbox = stb
#        request_bundle.data = bundle.data

        # Override the tech and operator fields
#        setattr(request_bundle.obj, 'settopbox', stb)
#        setattr(request_bundle.obj, 'channel', ch)

#        request_bundle = res.full_hydrate(request_bundle)
#        res.save(request_bundle)
 
    def filter_read_list(self, object_list, bundle):
        if bundle.request.user.is_anonymous() is True:
            return False
        user = str(bundle.request.user)
        serial = user.replace(settings.STB_USER_PREFIX, '')
        try:
            stb = models.SetTopBox.objects.get(serial_number=serial)
        except:
            log.error('No STB for user:%s', user)
            return False
        return object_list.filter(settopbox=stb)
    
    def read_list(self, object_list, bundle):
        return self.filter_read_list(object_list, bundle)

    def read_detail(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)

    #def create_list(self, object_list, bundle):
        #pdb.set_trace()
        #return self.create_object(object_list, bundle)
    
    def create_detail(self, object_list, bundle):
        return self.is_create_authorized(object_list, bundle)

    def update_list(self, object_list, bundle):
        return self.is_authorized(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self.is_authorized(object_list,bundle)

    def delete_list(self, object_list, bundle):
        return self.is_authorized(object_list,bundle)

    def delete_detail(self, object_list, bundle):
        return self.is_authorized(object_list,bundle)

class SetTopBoxConfigResource(NamespacedModelResource):

    class Meta:
        queryset = models.SetTopBoxConfig.objects.all()
        resource_name = 'settopboxconfig'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        fields = ['key', 'value', 'value_type']
        always_return_data = False
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
        log.debug('User=%s', request.user)
        if request.user.is_anonymous() is False:
            log.debug('user:%s', request.user)
            user = request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = models.SetTopBox.objects.get(serial_number=serial)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            if hasattr(self._meta.authorization, 'apply_limits'):
                object_list = self._meta.authorization.apply_limits(request,
                    object_list)
            object_list = object_list.filter(settopbox=stb)
        else:
            object_list = models.SetTopBoxConfig.objects.none()
        return object_list

    def obj_create(self, bundle, **kwargs):
        from django.db import transaction
        log.debug('New Parameter:%s=%s (%s)', bundle.data.get('key'),
            bundle.data.get('value'), bundle.data.get('value_type'))
        if bundle.request.user.is_anonymous() is False:
            user = bundle.request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = models.SetTopBox.objects.get(serial_number=serial)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            with transaction.atomic():
                try:
                    bundle = super(SetTopBoxConfigResource, self).obj_create(
                        bundle, settopbox=stb, **kwargs)
                except IntegrityError, e:
                    log.error('%s', e)
                    raise BadRequest(e)
                return bundle
        else:
            raise BadRequest('')
        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        from django.db import transaction
        log.debug('Update key:%s=%s (%s)', bundle.data.get('key'),
            bundle.data.get('value'), bundle.data.get('value_type'))
        if bundle.request.user.is_anonymous() is False:
            user = bundle.request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = models.SetTopBox.objects.get(serial_number=serial)
            self._meta.queryset.filter(settopbox=stb)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            # TODO: Não deixar um STB moduficar as configs de outro STB
            #print(bundle)
            #if bundle.obj.settopbox_id != stb.id:
            #    raise BadRequest('')
        with transaction.atomic():
            try:
                #print(dir(bundle.obj))
                bundle = super(SetTopBoxConfigResource, self).obj_update(bundle,
                    **kwargs)
            except IntegrityError, e:
                log.error('%s', e)
                raise BadRequest(e)
        return bundle

    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.user
        log.debug('User=%s', user)
        if user.is_anonymous() is False:
            if not user.is_staff:
                serial = user.username.replace(settings.STB_USER_PREFIX, '')
                log.debug('Serial=%s', serial)
                stb = models.SetTopBox.objects.get(serial_number=serial)
                log.debug('User:%s, SetTopBox:%s', user, stb)
                # self._meta.queryset.filter(settopbox=stb)
                obj_list = super(SetTopBoxConfigResource, self).obj_get_list(
                    bundle, **kwargs).filter(settopbox=stb)
        else:
            obj_list = models.SetTopBoxConfig.objects.none()
        return obj_list

    def obj_get(self, bundle, **kwargs):
        user = bundle.request.user
        log.debug('User=%s', user)
        obj_list = models.SetTopBoxConfig.objects.none()
        if user.is_anonymous() is False:
            if not user.is_staff:
                serial = user.username.replace(settings.STB_USER_PREFIX, '')
                log.debug('Serial=%s', serial)
                stb = models.SetTopBox.objects.get(serial_number=serial)
                log.debug('User:%s, SetTopBox:%s', user, stb)
                obj_list = super(SetTopBoxConfigResource, self).obj_get(
                    bundle, **kwargs)
                if obj_list.settopbox == stb:
                    return obj_list
                else:
                    #raise Unauthorized('')
                    obj_list = models.SetTopBoxConfig.objects.none()
        else:
            obj_list = models.SetTopBoxConfig.objects.none()
        return obj_list


class StreamRecorderResource(NamespacedModelResource):
    class Meta:
        queryset = devicemodels.StreamRecorder.objects.filter(status=True)


class APIKeyAuthorization(Authorization):
    # http://django-tastypie.readthedocs.org/en/latest/authorization.html

    def read_list(self, object_list, bundle):
        user = bundle.request.user
        log.debug('Readlist request to:%s', user)
        if user.is_anonymous():
            raise Unauthorized("Unauthorized")
        return object_list.filter(user=user)

    def read_detail(self, object_list, bundle):
        return not bundle.request.user.is_anonymous()

class APIKeyResource(NamespacedModelResource):
    class Meta:
        queryset = ApiKey.objects.all()
        authorization = APIKeyAuthorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            "key": ALL
        }


class SetTopBoxMessage(NamespacedModelResource):
    class Meta:
        queryset = models.SetTopBoxMessage.objects.all()

class SetTopBoxProgramScheduleResource(NamespacedModelResource):
    
    class Meta:
        queryset = models.SetTopBoxProgramSchedule.objects.all()
        resource_name = 'settopboxprogramschedule'
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        urlconf_namespace = 'client'
        fields = ['schedule_date', 'message', 'url']
        always_return_data = False
        filtering = {
            "schedule_date": ALL,
            "message": ALL,
            "url": ALL,
        }
        authorization = SetTopBoxApiAuth()
        validation = Validation()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(),
            BasicAuthentication(realm='cianet-middleware'),
            Authentication(),
            )

    def obj_create(self, bundle, **kwargs):
        from django.db import transaction
        if bundle.request.user.is_anonymous() is False:
            user = bundle.request.user
            serial = user.username.replace(settings.STB_USER_PREFIX, '')
            stb = models.SetTopBox.objects.get(serial_number=serial)
            channel = bundle.data.get('channel')
            ch = models.Channel.objects.get(number=channel)
            log.debug('User:%s, SetTopBox:%s', user, stb)
            with transaction.atomic():
                try:
                    bundle = super(SetTopBoxProgramScheduleResource, self).obj_create(
                        bundle, settopbox=stb, channel=ch, **kwargs)
                except IntegrityError, e:
                    log.error('%s', e)
                    raise BadRequest(e)
                return bundle
        else:
            raise BadRequest('')
        return bundle
    
api = NamespacedApi(api_name='v1', urlconf_namespace='client_v1')
api.register(SetTopBoxResource())
api.register(SetTopBoxParameterResource())
api.register(SetTopBoxChannelResource())
api.register(SetTopBoxConfigResource())
api.register(APIKeyResource())
api.register(SetTopBoxMessage())
api.register(SetTopBoxProgramScheduleResource())

apis = [api]
