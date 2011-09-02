#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# Requisições de JSON para atualizar estatisticas do Push-server
import simplejson
import urllib2

class PushStream(object):
    """
    
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # TODO: Passar parametros e fazer a conexão logo na primeira instancia
            cls._instance = super(PushStream, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    loaded = False
    
    class CACHE_TYPES():
        NONE = 0
        PER_VIEW = 1
        PER_TIME = 2
    
    class config():
        # Connection settings
        schema     = "http"
        hostname   = "127.0.0.1"
        port       = 80
        publisher  = "pub/"
        subscriber = "sub/"
        stats      = "channels-stats/"
        connected  = False
    cache_type = CACHE_TYPES.PER_VIEW
    
    class data():
        hostname = None
        time = None
        channels = 0
        broadcast_channels = 0
        published_messages = 0
        subscribers = 0
        stored_messages = 0
        workers = []
        channels_list = {}
        
    class worker():
        pid = 0
        subscribers = 0
        
    class channel(object):
        name = ''
        published_messages = 0
        stored_messages = 0
        subscribers = 0
        def __str__(self):
            return self.name

    def connect(self, **kwargs):
        """
        Conecta com o XML referente ao pushstream server,
        deve povoar as propriedades da classe `data`
        
        Os kwargs de configuração são referentes a classe `config`
        
        Se o XML não for encontrado, ou retornar algum tipo de erro,
        o urllib2 vai disparar um exception, deve ser tratado por try-except
        """
        for key in kwargs:
            # Só recnonecta se mudar alguma configuração
            if getattr(self.config, key) != kwargs[key]: 
                self.loaded = False
            setattr(self.config, key, kwargs[key])
        self._load()
    
    def server_url(self):
        return "%s://%s%s/" % (
            self.config.schema, 
            self.config.hostname, 
            ((":%d" % (self.config.port)) if self.config.port else '' )
        )
    
    def _load(self):
        if self.loaded: 
            return self
        # TODO: implementar cache
        request     = urllib2.Request("%s%s?id=ALL" % 
                                      (self.server_url(), self.config.stats))
        opener      = urllib2.build_opener()
        file_stream = opener.open(request)
        json        = simplejson.load(file_stream)
        
        self.data.hostname = json.get("hostname")
        self.data.time = json.get("time")
        self.data.channels = int(json.get("channels"))
        self.data.broadcast_channels = int(json.get("broadcast_channels"))
        self.data.channels_list = {}

        for channel in json.get("infos"):
            channel_obj = self.channel()
            channel_obj.name               = channel.get("channel")
            channel_obj.published_messages = int(channel.get("published_messages"))
            channel_obj.stored_messages    = int(channel.get("stored_messages"))
            channel_obj.subscribers        = int(channel.get("subscribers"))
            self.data.channels_list[str(channel_obj)] = channel_obj 
            # Dados totais
            self.data.published_messages += channel_obj.published_messages 
            self.data.stored_messages    += channel_obj.stored_messages
            self.data.subscribers        += channel_obj.subscribers
                    
        self.loaded = True
        return self