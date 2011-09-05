#!/usr/bin/env python
#coding:utf8

from django.db                import models
from fields                   import MACAddressField
from django.utils.translation import ugettext as _

from lib.pushstream.pushstream import PushStream

import urllib2

################################################################################
# Utils                                                                        #
################################################################################

class ToggleSignal():
    """ Singleton pra gerenciar toggle entre signals, para livrar um pouco as
    execuções desnecessárias no acesso de instancias filho que contenham um signal
    connectado a ela.
    
    !CUIDADO!
    Não vai desconectar e após o processo esquecer de reconectar, senão ele perde
    o sinal apartir do momento que sai do processo. """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """ Singleton """
        if not cls._instance:
            cls._instance = super(ToggleSignal, cls).__new__(cls, *args, **kwargs)
        cls._instance.connect = None
        cls._instance.receiver = None
        cls._instance.sender = None
        cls._instance.weak = True
        cls._instance.dispatch_uid = None
        return cls._instance
    
    def _toggler(self, last_state):
        """ Toggler de signal interno """
        if last_state:
            models.signals.post_init.connect(self.connect, 
                                             sender = self.sender,
                                             weak = self.weak,
                                             dispatch_uid = self.dispatch_uid)
            return False
        else:
            models.signals.post_init.disconnect(self.receiver, 
                                                self.sender, 
                                                self.weak, 
                                                self.dispatch_uid)
            return True
    _setupbox_post_init = False
    def setupbox_post_init(self, **kwargs):
        """ Define toggler pro setupbox_post_init """
        self.connect = SetupBox._post_init
        self.sender = SetupBox
        self.dispatch_uid = "SetupBox._post_init"
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self._setupbox_post_init = self._toggler(self._setupbox_post_init)
        
    _pushserver_post_init = False
    def pushserver_post_init(self, **kwargs):
        """ Define toggler pro setupbox_post_init """
        self.connect = PushServer._post_init
        self.sender = PushServer
        self.dispatch_uid = "PushServer._post_init"
        for key in kwargs:
            setattr(self, key, kwargs[key])

################################################################################
# Pessoa                                                                       #
################################################################################

class Pessoa(models.Model):
    """ Modelo que define a pessoa responsável por um setup box? """
    nome = models.CharField(_('Nome'), 
                            max_length = 200)

################################################################################
# PushServer                                                                   #
################################################################################

class PushServer(models.Model):
    """ Modelo que persiste dados do Http-Push-Stream server """
    schema = models.CharField(_(u'Protocolo'), 
                              max_length = 5, 
                              default = 'http', 
                              blank = False)
    address = models.CharField(_(u'Endereço do servidor'), 
                               max_length = 255, 
                               unique = True)
    port = models.IntegerField(_(u'Porta'), 
                               default = 80)
    broadcast_channel = models.CharField(_(u'Canal de Broadcast'), 
                                         default = 'broadcast', 
                                         max_length = 40, 
                                         blank = False)
    hostname = models.CharField(_(u'Nome do servidor'), 
                                max_length = 255, 
                                editable = False)
    publisher_link = models.CharField(_(u'Link do Publicador'), 
                                      max_length = 20, 
                                      default = '/pub?id=', 
                                      blank = False)
    subscriber_link = models.CharField(_(u'Link de Inscrição'), 
                                       max_length = 20, 
                                       default = '/sub', 
                                       blank = False)
    #time = models.DateTimeField(_('Time'))
    channels = models.IntegerField(_(u'Canais'), 
                                   default = 0, 
                                   editable = False)
    broadcast_channels = models.IntegerField(_(u'Broadcast Channels'), 
                                             default = 0, 
                                             editable = False)
    subscribers = models.IntegerField(_(u'Subscribers'), 
                                      default = 0, 
                                      editable = False)
    published_messages = models.IntegerField(_(u'Published Messages'), 
                                             default = 0, 
                                             editable = False)
    online = models.BooleanField(_(u'Online'), 
                                 default = False, 
                                 editable = False)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    updated = models.DateTimeField(_(u"Atualizado em"), 
                                   auto_now = True, 
                                   editable = False)
    def __unicode__(self):
        return u'%s://%s:%d (%s) [%d/%d/%d/%d]' % (self.schema, 
                                                   self.address, 
                                                   self.port, 
                                                   self.hostname, 
                                                   self.channels, 
                                                   self.broadcast_channels, 
                                                   self.subscribers, 
                                                   self.published_messages)
    def url(self, *args):
        if args[0] == 'pub':
            return u'%s://%s:%d%s' % (self.schema, 
                                      self.address, 
                                      self.port, 
                                      self.publisher_link)
        if args[0] == 'sub':
            return u'%s://%s:%d%s' % (self.schema, 
                                      self.address, 
                                      self.port, 
                                      self.subscriber_link)
        return u'%s://%s:%d' % (self.schema, self.address, self.port)
    def setupboxes(self):
        return SetupBox.objects.filter(pushserver = self.pk).count()
    class Meta:
        verbose_name        = _(u"Push Server")
        verbose_name_plural = _(u"Push Servers")
        ordering            = ['-channels', '-subscribers']
    
    @staticmethod
    def _post_init(signal, instance, sender, **kwargs):
        """ Adiciona lista de SetupBox ao PushServer, verificando pelo json do 
        push_stream """
        if not instance.pk or not instance.port or not instance.address: return
        pushserver = PushStream()
        try:
            pushserver.connect(port = instance.port, hostname = instance.address)
            instance.broadcast_channels = pushserver.data.broadcast_channels
            instance.channels           = pushserver.data.channels
            instance.hostname           = pushserver.data.hostname
            instance.published_messages = pushserver.data.published_messages
            instance.stored_messages    = pushserver.data.stored_messages
            instance.subscribers        = pushserver.data.subscribers
            instance.online             = True
            for channel in pushserver.data.channels_list:
                try:
                    #Desconectar signals, não são necessários aqui
                    ToggleSignal().setupbox_post_init()
                    setupbox = SetupBox(
                        pushserver = instance,
                        mac = channel)
                    #Reconecta signals
                    ToggleSignal().setupbox_post_init()
                    setupbox.clean_fields()
                    setupbox.save()
                    
                    
                except: print "Falhou ao criar (provavelmente já existe): "+channel
        except: 
            instance.online = False
        instance.save()
        print "PushServer post_init signal executed."

models.signals.post_init.connect(PushServer._post_init, 
                                 sender = PushServer,
                                 dispatch_uid = "PushServer._post_init")

class PushServerCommands(models.Model):
    """ Modelo que armazena comandos enviados para canal de broadcast de um
    PushServer (deverá ser enviado a todos setupbox que estiverem online) """
    pushserver = models.ForeignKey(PushServer)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    updated = models.DateTimeField(_(u"Atualizado em"), 
                                   auto_now = True, 
                                   editable = False)
    command = models.TextField(_(u"Comando"), 
                               blank = False)
    response = models.TextField(_(u"Resposta"), 
                                blank = True,
                                editable = False)
    sended = models.BooleanField(_(u"Enviado"), 
                                 default = False,
                                 editable = False)
    ping = models.BooleanField(_(u"Solicitar retorno (ping)"), 
                               default = False)

################################################################################
# SetupBox                                                                     #
################################################################################

class SetupBox(models.Model):
    """ Modelo do SetupBox, filho do PushServer """
    pushserver = models.ForeignKey(PushServer)
    mac = MACAddressField(_(u'MAC Address'),
                          blank = False,
                          unique = True)
    connected = models.BooleanField(_(u'Connected'),
                                    default = False,
                                    editable = False)
    enabled = models.BooleanField(_(u'Enabled'),
                                  default  = False)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    updated = models.DateTimeField(_(u"Atualizado em"), 
                                   auto_now = True, 
                                   editable = False)
    def __unicode__(self):
        return self.mac
    class Meta:
        verbose_name        = _("SetupBox")
        verbose_name_plural = _("SetupBoxes")
        ordering            = ['-enabled', '-connected', 'mac']
        
    @staticmethod
    def _post_init(signal, instance, sender, **kwargs):
        """ Atualiza status de conexão do setupbox na instancia, se for 
        diferefente o status ele salva """
        if not instance.mac: return
        pushserver = PushStream()
        #Desconecta sinal do pushserver
        ToggleSignal().pushserver_post_init()
        try:
            
            pushserver.connect(port = instance.pushserver.port, 
                               hostname = instance.pushserver.address)
            channel = pushserver.data.channels_list[instance.mac]
            instance.connected = bool(channel.subscribers) 
        except:
            instance.connected = False
        try:
            instance.clean_fields()
            instance.save()
        except: pass
        #Connecta sinal do pushserver
        ToggleSignal().pushserver_post_init()
        print "SetupBox post_init signal executed."
        
models.signals.post_init.connect(SetupBox._post_init, 
                                 sender = SetupBox,
                                 dispatch_uid = "SetupBox._post_init")

class SetupBoxCommands(models.Model):
    """ Modelo que armazena comandos enviados para cada setupbox """
    setupbox = models.ForeignKey(SetupBox)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    command = models.TextField(_(u"Comando"), 
                               blank = False)
    response = models.TextField(_(u"Resposta"), 
                                blank = True,
                                editable = False)
    sended = models.BooleanField(_(u"Enviado"), 
                                  default = False,
                                  editable = False)
    ping = models.BooleanField(_(u"Solicitar retorno (ping)"), 
                               default = False)
    def online_setupbox(self):
        online = u''
        for setupbox in self.pushservercommandssetupbox_set:
            online += u", " if online != '' else u''
            online += u"%s" % setupbox.mac
        return online

class SetupBoxCommandsResponse(models.Model):
    """ Modelo que armazena respostas do setupbox quando habilitado ping no
    modelo SetupBoxCommands. """
    setupboxcommands = models.ForeignKey(SetupBoxCommands)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    server_release = models.DateTimeField(_(u"Momento que servidor disparou"),
                                          editable = False)
    response_message = models.TextField(_(u"Mensagem na resposta"), 
                                        blank = True,
                                        editable = False)
    def server_delay(self):
        return (self.server_release - self.setupboxcommands.created)
    
    def setupbox_delay(self):
        return (self.created - self.server_release)
    
    def total_delay(self):
        return (self.setupboxcommands.created - self.created)

################################################################################
# PushServer + SetupBox                                                        #
################################################################################

class PushServerCommandsSetupBox(models.Model):
    """ Modelo que armazena referencia dos setupboxes que estavam conectados na
    hora do envio de um comando em broadcast pelo PushServer """
    pushservercommands = models.ForeignKey(PushServerCommands)
    setupbox = models.ForeignKey(SetupBox)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)

class PushServerCommandsResponse(models.Model):
    """ Modelo que armazena respostas do setupbox quando habilitado ping no
    modelo PushServerCommands. """
    pushservercommands = models.ForeignKey(PushServerCommands)
    setupbox = models.ForeignKey(SetupBox)
    created = models.DateTimeField(_(u"Criado em"), 
                                   auto_now_add = True, 
                                   editable = False)
    server_release = models.DateTimeField(_(u"Momento que servidor disparou"),
                                          editable = False)
    response_message = models.TextField(_(u"Mensagem na resposta"), 
                                        blank = True,
                                        editable = False)
    def server_delay(self):
        return (self.server_release - self.setupboxcommands.created)
    
    def setupbox_delay(self):
        return (self.created - self.server_release)
    
    def total_delay(self):
        return (self.setupboxcommands.created - self.created)

def _pre_save_push_server_command(signal, instance, sender, **kwargs):
    """ Antes de salvar na base de dados, executa requisição na URL de
    publicação do PushServer referente ao setupbox"""
    if isinstance(instance, SetupBoxCommands):
        url = instance.setupbox.pushserver.url('pub')
        channel = instance.setupbox.mac
    elif isinstance(instance, PushServerCommands):
        url = instance.pushserver.url('pub')
        channel = instance.pushserver.broadcast_channel
        
        def _post_save_push_server_command(signal, instance, sender, **kwargs):
            models.signals.post_save.disconnect(instance, sender)
            for setupbox in SetupBox.objects.filter(pushserver = instance.pushserver,
                                                    connected = True):
                online = PushServerCommandsSetupBox(pushservercommands = instance,
                                                    setupbox = setupbox)
                online.save()
        models.signals.post_save.connect(_post_save_push_server_command, sender = PushServerCommands)
    else:
        print "Instancia inválida para o signal"
        return
    url += channel
    
    command = ''
    if isinstance(instance, SetupBoxCommands) and instance.ping:
        command += "r();"
    command += instance.command
    
    try:
        request  = urllib2.Request(url, command)
        response = urllib2.urlopen(request)
        instance.sended = True
        content  = response.read()
        instance.response = content
        print u"Enviado comando pro canal [%s]: \n" \
            "Request: \n" \
            "%s \n" \
            "==========================================\n" \
            "Response Content:\n" \
            "%s" % (
              channel, command, content)
    except:
        instance.sended = False

models.signals.pre_save.connect(_pre_save_push_server_command, 
                                sender = SetupBoxCommands)
models.signals.pre_save.connect(_pre_save_push_server_command, 
                                sender = PushServerCommands)