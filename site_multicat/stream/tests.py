#!/usr/bin/env python
# -*- encoding:utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class PlayerTest(TestCase):
    
    def test_play(self):
        from stream import models
        from stream.player import Player
        p = Player()
        source = models.MediaMulticastSource(name='s1',ip='239.0.1.1',port=30000,is_rtp=False)
        destination = models.MediaMulticastDestination(name='d1',ip='224.0.0.1',port=5000,is_rtp=False)
        s1 = models.Stream(source=source,destination=destination,pid=None)
        pid = p.play_stream(s1)
        s1.pid = pid
        self.assertGreater(pid, 0, 'O numero do processo deveria ser maior que 0')
        if pid:
            p.stop_stream(s1)
        l = p.list_running()
        self.assertEqual(len(l), 0, 'A lista de processos deveria ser vazia')
            
    def test_runnig(self):
        from stream import models
        from stream.player import Player
        p = Player()
        s1 = models.MediaMulticastSource(name='s1',ip='239.0.1.1',port=30000,is_rtp=False)
        s2 = models.MediaMulticastSource(name='s2',ip='239.0.1.1',port=30000,is_rtp=False)
        s3 = models.MediaMulticastSource(name='s3',ip='239.0.1.1',port=30000,is_rtp=False)
        s1.save()
        s2.save()
        s3.save()
        d1 = models.MediaMulticastDestination(name='d1',ip='224.0.0.1',port=5000,is_rtp=False)
        d2 = models.MediaMulticastDestination(name='d2',ip='224.0.0.1',port=5001,is_rtp=False)
        d3 = models.MediaMulticastDestination(name='d3',ip='224.0.0.1',port=5002,is_rtp=False)
        d1.save()
        d2.save()
        d3.save()
        a = models.Stream(source=s1,destination=d1,pid=None)
        b = models.Stream(source=s2,destination=d2,pid=None)
        c = models.Stream(source=s3,destination=d3,pid=None)
        #a.save()
        #b.save()
        #c.save()
        pida = p.play_stream(a)
        a.pid = pida
        a.save()
        pidb = p.play_stream(b)
        b.pid = pidb
        b.save() 
        pidc = p.play_stream(c)
        c.pid = pidc
        c.save()
        ## Busca listagem dos processos rodando
        l = p.list_running()
        self.assertGreater(pida, 0, 'O numero do processo deveria ser maior que 0')
        self.assertEqual(len(l), 3, 'Deveria haver 3 processos')
        # Matando o b
        p.stop_stream(b)
        self.assertFalse(p.is_playing(b), 'O processo b deveria estar morto')
        l1 = p.list_running()
        self.assertEqual(len(l1), 2, 'Deveria haver 2 processos')
        p.kill_all()
        l2 = p.list_running()
        self.assertEqual(len(l2), 0, 'Deveria ser 0 o número de processos')
    
    def test_control_stream(self):
        from stream import models
        origin = models.MediaMulticastSource()
        origin.name = 'Origem teste'
        origin.ip = '239.0.0.10'
        origin.port = 11001
        origin.is_rtp = False
        origin.save()
        dest = models.MediaMulticastDestination()
        dest.name = 'Destino teste'
        dest.ip = '192.168.0.1'
        dest.port = 8888
        dest.is_rtp = False
        dest.save()
        s = models.Stream(source=origin,destination=dest,pid=None)
        ## Salvando o stream
        s.save()
        from player import Player
        p = Player()
        
        pid = p.play_stream(s)
        s.pid = pid
        s.save()
        self.assertGreater(pid,0, 'O pid deveria ser maior que 0')
        p.stop_stream(s)
        l = p.list_running()
        self.assertEqual(len(l), 0, 'A lista de processos deveria ser vazia')
        

