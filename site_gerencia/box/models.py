#!/usr/bin/env python
#coding:utf8

from django.db                import models
from fields                   import MACAddressField
from django.utils.translation import ugettext as _

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

def connected_get(signal,instance,sender,**kwargs):
    """
    Exibe texto referente ao ID do status atual
    """
    import simplejson
    import urllib2
    
    try:
        req = urllib2.Request("http://127.0.0.1:8080/channels-stats/?id=%s" % instance.mac)
        opener = urllib2.build_opener()
        f = opener.open(req)
        json = simplejson.load(f)
    except: 
        pass

    try:
        if int(json.get('subscribers')) > 0:
            instance.connected = True
            instance.save()
            return
    except: 
        pass
    instance.connected = False
    instance.save()

models.signals.post_init.connect(connected_get, sender=SetupBox)

class Pessoa(models.Model):
    """
    Modelo que define a pessoa responsável por um setup box?
    """
    nome = models.CharField(_('Nome'), max_length = 200)


class PushServer(models.Model):
    """ Modelo que persiste dados do Http-Push-Stream server """
    hostname = models.CharField(_('Hostname'), max_length = 255)
    #time = models.DateTimeField(_('Time'))
    channels = models.IntegerField(_('Channels'))
    broadcast_channels = models.IntegerField(_('Broadcast Channels'))
    published_messages = models.IntegerField(_('Published Messages'))
    subscribers = models.IntegerField(_('Subscribers'))
    def __unicode__(self):
        return u'%s [%d/%d] %d' % (self.hostname, self.channels, self.subscribers, self.published_messages)
    # TODO: Sobrescrever método de leitura, para que ele leia o JSON e salve na base, 
    # caso não seja possível, tem que apenas ler o último registro
    class Meta:
        verbose_name        = _("Push Server")
        verbose_name_plural = _("Push Servers")
        ordering            = ['-subscribers']

