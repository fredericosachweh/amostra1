#!/usr/bin/env python
#coding:utf8

from django.db                import models
from fields                   import MACAddressField
from django.utils.translation import ugettext as _

# Requisições de JSON para atualizar estatisticas do Push-server
import simplejson
import urllib2

class SetupBox(models.Model):
    """
    Modelo que define campos, propriedades e comportamento do SetupBox
    """
    mac = MACAddressField(_(u'MAC Address'), blank = False, unique = True)
    connected = models.BooleanField(_(u'Connected'), default  = False, editable = False)
    enabled = models.BooleanField(_(u'Enabled'), default = False)
    
    def __unicode__(self):
        return self.mac
    class Meta:
        verbose_name        = _("SetupBox")
        verbose_name_plural = _("SetupBoxes")
        ordering            = ['-enabled', '-connected', 'mac']

    @staticmethod
    def update_connected_field(signal,instance,sender,**kwargs):
        """
        Exibe texto referente ao ID do status atual
        """
        try:
            req = urllib2.Request("http://127.0.0.1:8080/channels-stats/?id=%s" % instance.mac)
            opener = urllib2.build_opener()
            f = opener.open(req)
            json = simplejson.load(f)
            instance.connected = True if int(json.get('subscribers')) > 0 else False
        except: 
            instance.connected = False
        
        
        
        instance.save()

models.signals.post_init.connect(SetupBox.update_connected_field, sender=SetupBox)

class Pessoa(models.Model):
    """
    Modelo que define a pessoa responsável por um setup box?
    """
    nome = models.CharField(_('Nome'), max_length = 200)


class PushServer(models.Model):
    """ Modelo que persiste dados do Http-Push-Stream server """
    hostname = models.CharField(_(u'Nome do servidor'), max_length = 255)
    port = models.IntegerField(_(u'Porta'), default  = 80)
    #time = models.DateTimeField(_('Time'))
    channels = models.IntegerField(_(u'Canais'), default  = 0, editable = False)
    broadcast_channels = models.IntegerField(_(u'Broadcast Channels'), default  = 0, editable = False)
    published_messages = models.IntegerField(_(u'Published Messages'), default  = 0, editable = False)
    subscribers = models.IntegerField(_(u'Subscribers'), default  = 0, editable = False)
    def __unicode__(self):
        return u'%s [%d/%d] %d' % (self.hostname, self.channels, self.subscribers, self.published_messages)
    # TODO: Sobrescrever método de leitura, para que ele leia o JSON e salve na base, 
    # caso não seja possível, tem que apenas ler o último registro
    class Meta:
        verbose_name        = _(u"Push Server")
        verbose_name_plural = _(u"Push Servers")
        ordering            = ['-subscribers']
    @staticmethod
    def update_from_json(signal,instance,sender,**kwargs):
        """
        Exibe texto referente ao ID do status atual
        """
        if instance.hostname == '':
            return;
        
        try:
            req = urllib2.Request("http://%s%s/channels-stats/?id=ALL" % instance.hostname, (':'+str(instance.port) if instance.port else '') )
            opener = urllib2.build_opener()
            f = opener.open(req)
            json = simplejson.load(f)
        except: 
            print u"Erro, não foi possível carregar url com status do canal: %s" % instance.hostname
            return
    
        try:
            if int(json.get('subscribers')) > 0:
                instance.connected = True
                instance.save()
                return
        except: 
            pass
        instance.connected = False
        instance.save()

models.signals.post_init.connect(PushServer.update_from_json, sender=PushServer)



