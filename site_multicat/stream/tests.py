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
        from stream.player import Player
        p = Player()
        proc = p.play('224.0.0.1', 30000, '239.0.1.1', 10000, 50000)
        if proc.pid:
            #print('PID:%d'%proc.pid)
            proc.kill()
    def test_runnig(self):
        from stream.player import Player
        p = Player()
        a = p.play('224.0.0.1', 30000, '239.0.1.1', 10001, 50001)
        b = p.play('224.0.0.1', 30000, '239.0.1.1', 10002, 50002)
        c = p.play('224.0.0.1', 30000, '239.0.1.1', 10003, 50003)
        ## Busca listagem dos processos rodando
        l = p.list_running()
        self.assertTrue(l.count(a) is 1, 'Deveria ser 1 o numero de processos a')
        self.assertTrue(l.count(b) is 1, 'Deveria ser 1 o numero de processos b')
        self.assertTrue(l.count(c) is 1, 'Deveria ser 1 o numero de processos c')
        self.assertGreater(a.pid, 0, 'O numero do processo deveria ser maior que 0')
        self.assertEqual(len(l), 3, 'Deveria haver 3 processos')
        # Matando o b
        b.kill()
        b.wait(1)
        self.assertFalse(b.is_running(), 'O processo b deveria estar morto')
        l1 = p.list_running()
        self.assertEqual(len(l1), 2, 'Deveria haver 2 processos')
        p.kill_all()
        a.wait(1)
        c.wait(1)
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
        ##
        s.save()
        

