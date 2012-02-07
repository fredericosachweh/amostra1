#!/usr/bin/env python
# -*- encoding:utf-8 -*-
#
#from django.conf import settings
#from django.test import TestCase, Client
#from django.core.urlresolvers import reverse
#
#class PlayerTest(TestCase):
#    def setUp(self):
#        pass
#        #print('No setUp')
#    
#    def tearDown(self):
#        pass
#        #print('No tearDown')
#    
#    def test_play(self):
#        from stream import models
#        from stream.player import Player
#        p = Player()
#        source = models.MediaMulticastSource(name='s1',ip='239.0.1.1',port=30000,is_rtp=False)
#        destination = models.MediaMulticastDestination(name='d1',ip='224.0.0.1',port=5000,is_rtp=False)
#        s1 = models.Stream(source=source,destination=destination,pid=None)
#        pid = p.play_stream(s1)
#        s1.pid = pid
#        self.assertGreater(pid, 0, 'O numero do processo deveria ser maior que 0')
#        if pid:
#            p.stop_stream(s1)
#        l = p.list_running()
#        self.assertEqual(len(l), 0, 'A lista de processos deveria ser vazia')
#            
#    def test_runnig(self):
#        from stream import models
#        from stream.player import Player
#        p = Player()
#        s1 = models.MediaMulticastSource(name='s1',ip='239.0.1.1',port=30000,is_rtp=False)
#        s2 = models.MediaMulticastSource(name='s2',ip='239.0.1.1',port=30000,is_rtp=False)
#        s3 = models.MediaMulticastSource(name='s3',ip='239.0.1.1',port=30000,is_rtp=False)
#        s1.save()
#        s2.save()
#        s3.save()
#        d1 = models.MediaMulticastDestination(name='d1',ip='224.0.0.1',port=5000,is_rtp=False)
#        d2 = models.MediaMulticastDestination(name='d2',ip='224.0.0.1',port=5001,is_rtp=False)
#        d3 = models.MediaMulticastDestination(name='d3',ip='224.0.0.1',port=5002,is_rtp=False)
#        d1.save()
#        d2.save()
#        d3.save()
#        a = models.Stream(source=s1,destination=d1,pid=None)
#        b = models.Stream(source=s2,destination=d2,pid=None)
#        c = models.Stream(source=s3,destination=d3,pid=None)
#        #a.save()
#        #b.save()
#        #c.save()
#        pida = p.play_stream(a)
#        a.pid = pida
#        a.save()
#        pidb = p.play_stream(b)
#        b.pid = pidb
#        b.save() 
#        pidc = p.play_stream(c)
#        c.pid = pidc
#        c.save()
#        ## Busca listagem dos processos rodando
#        l = p.list_running()
#        self.assertGreater(pida, 0, 'O numero do processo deveria ser maior que 0')
#        self.assertEqual(len(l), 3, 'Deveria haver 3 processos')
#        # Matando o b
#        p.stop_stream(b)
#        self.assertFalse(p.is_playing(b), 'O processo b deveria estar morto')
#        l1 = p.list_running()
#        self.assertEqual(len(l1), 2, 'Deveria haver 2 processos')
#        p.kill_all()
#        l2 = p.list_running()
#        self.assertEqual(len(l2), 0, 'Deveria ser 0 o número de processos')
#    
#    def test_control_stream(self):
#        from stream import models
#        origin = models.MediaMulticastSource()
#        origin.name = 'Origem teste'
#        origin.ip = '239.0.0.10'
#        origin.port = 11001
#        origin.is_rtp = False
#        origin.save()
#        dest = models.MediaMulticastDestination()
#        dest.name = 'Destino teste'
#        dest.ip = '192.168.0.1'
#        dest.port = 8888
#        dest.is_rtp = False
#        dest.save()
#        s = models.Stream(source=origin,destination=dest,pid=None)
#        ## Salvando o stream
#        s.save()
#        from player import Player
#        p = Player()
#        
#        pid = p.play_stream(s)
#        s.pid = pid
#        s.save()
#        self.assertGreater(pid,0, 'O pid deveria ser maior que 0')
#        p.stop_stream(s)
#        l = p.list_running()
#        self.assertEqual(len(l), 0, 'A lista de processos deveria ser vazia')
#
#
#class DVBTestMAC(TestCase):
#    """
#    Teste de link entre o device DVB
#    """
#    def test_get_adapter(self):
#        import os
#        if not os.path.exists('/dev/dvb'):
#            return
#        # a1 = 00:18:BD:5D:DE:14 
#        # a0 = 00:18:BD:5D:D9:F4
#        f0 = open('/dev/dvb/adapter0.mac','w')
#        f1 = open('/dev/dvb/adapter1.mac','w')
#        f0.write('00:18:BD:5D:D9:F4\n')
#        f1.write('00:18:BD:5D:DE:14\n')
#        f0.close()
#        f1.close()
#        
#        from models import DVBSource
#        dvb0 = DVBSource.objects.create(name='Teste 0',device='-f 3390000 -s 7400000 -m psk_8 -U -u -d 239.0.1.1:10000',hardware_id='00:18:BD:5D:D9:F4')
#        dvb1 = DVBSource.objects.create(name='Teste 1',device='-f 3274000 -s 5926000 -U -u -d 239.0.1.2:10000',hardware_id='00:18:BD:5D:DE:14')
#        dvb0.save()
#        dvb1.save()
#        self.assertEqual(dvb0.get_adapter(), 0, 'O adaptador deveria ser o 0')
#        self.assertEqual(dvb1.get_adapter(), 1, 'O adaptador deveria ser o 1')
#        
#        
#
#class DVBTest(TestCase):
#    """
#    Testes do device dvb
#    """
#    
#    def setUp(self):
#        from models import DVBSource, DVBDestination
#        ## Remover todos os sources
#        #DVBSource.objects.all().delete()
#        #print(DVBSource.objects.all())
#    def tearDown(self):
#        pass
#        
#    def test_parse(self):
#        from player import parse_dvb
#        cmd = """DVBlast 2.0.0 (git-379e8c5)
#warning: restarting
#debug: binding socket to 239.0.1.10:10000
#debug: conf: 224.0.0.17:10000/udp config=0x9 sid=1 pids[0]
#frontend has acquired lock
#debug: new RTP source: 68.84.65.160
#new RTP source: 68.84.65.160
#debug: Dump is 1316206720 seconds late - reset timing
#debug: new PAT tsid=1 version=0
#debug:   * program number=1 pid=80
#debug: end PAT
#debug: new PMT program=1 version=0 pcrpid=256
#debug:   * ES pid=256 streamtype=0x1b
#debug:     - desc 52 unknown
#debug:   * ES pid=512 streamtype=0x3
#debug:     - desc 52 unknown
#debug: end PMT
#"""
#        proglist = parse_dvb(cmd)
#        #print(proglist)
#        self.assertEqual(len(proglist), 1, 'Deveria hever 1 programa')
#        cmd1 = """DVBlast 2.0.0 (git-1.2-122-g379e8c5)
#warning: restarting
#warning: raw UDP output is deprecated.  Please consider using RTP.
#warning: for DVB-IP compliance you should use RTP.
#debug: using linux-dvb API version 5
#debug: Frontend "SL SI21XX DVB-S" type "QPSK (DVB-S/S2)" supports:
#debug:  frequency min: 950000, max: 2150000, stepsize: 125, tolerance: 0
#debug:  symbolrate min: 1000000, max: 45000000, tolerance: 500
#debug:  capabilities:
#debug:   INVERSION_AUTO
#debug:   FEC_1_2
#debug:   FEC_2_3
#debug:   FEC_3_4
#debug:   FEC_5_6
#debug:   FEC_7_8
#debug:   FEC_AUTO
#debug:   QPSK
#debug: frequency 3074000 is in C-band (lower)
#debug: configuring LNB to v=13 p=0 satnum=0
#debug: tuning QPSK frontend to f=3074000 srate=6666000 inversion=-1 fec=999 rolloff=35 modulation=legacy pilot=-1
#warning: failed opening CAM device /dev/dvb/adapter4/ca0 (No such file or directory)
#debug: setting filter on PID 0
#debug: setting filter on PID 16
#debug: setting filter on PID 17
#debug: setting filter on PID 18
#debug: setting filter on PID 19
#debug: setting filter on PID 20
#debug: conf: 239.0.1.6:10000/udp config=0x9 sid=0 pids[0]
#debug: conf: 239.0.1.7:10000/udp config=0x9 sid=1 pids[0]
#debug: conf: 239.0.1.8:10000/udp config=0x9 sid=2 pids[0]
#debug: frontend has acquired signal
#debug: frontend has acquired carrier
#debug: frontend has acquired stable FEC
#debug: frontend has acquired sync
#info: frontend has acquired lock
#frontend has acquired lock
#debug: - Bit error rate: 236
#debug: - Signal strength: 50688
#debug: - SNR: 0
#debug: Dump is 1316395400 seconds late - reset timing
#
#debug: setting filter on PID 32
#debug: setting filter on PID 259
#debug: new PAT tsid=0 version=7
#debug:   * NIT pid=16
#debug:   * program number=1 pid=32
#debug:   * program number=2 pid=259
#debug: end PAT
#debug: setting filter on PID 389
#debug: setting filter on PID 390
#debug: setting filter on PID 391
#debug: new PMT program=2 version=0 pcrpid=389
#debug:   * ES pid=389 streamtype=0x2
#debug:   * ES pid=390 streamtype=0x3
#debug:   * ES pid=391 streamtype=0x3
#debug:     - desc 0a language=SAP audiotype=0x0
#debug: end PMT
#debug: setting filter on PID 289
#debug: setting filter on PID 290
#debug: setting filter on PID 350
#debug: setting filter on PID 291
#debug: new PMT program=1 version=0 pcrpid=289
#debug:   * ES pid=289 streamtype=0x2
#debug:   * ES pid=290 streamtype=0x3
#debug:   * ES pid=350 streamtype=0x3
#debug:   * ES pid=291 streamtype=0x3
#debug:     - desc 0a language=SAP audiotype=0x0
#debug: end PMT
#debug: new SDT actual tsid=0 version=5 onid=1
#debug:   * service sid=1 eit present running=4
#debug:     - desc 48 type=0x1 provider="Impsat" service="TV Justica"
#debug:   * service sid=2 eit present running=4
#debug:     - desc 48 type=0x1 provider="" service="TV Justica 2"
#debug: end SDT
#debug: new NIT actual networkid=1 version=0
#debug: end NIT
#"""
#        proglist = parse_dvb(cmd1,debug=False)
#        #print(proglist)
#        self.assertEqual(len(proglist), 2, 'Deveria hever 2 programas')
#        cmd3 = """DVBlast 2.0.0 (git-1.2-122-g379e8c5)
#warning: restarting
#debug: using linux-dvb API version 5
#debug: Frontend "SL SI21XX DVB-S" type "QPSK (DVB-S/S2)" supports:
#debug:  frequency min: 950000, max: 2150000, stepsize: 125, tolerance: 0
#debug:  symbolrate min: 1000000, max: 45000000, tolerance: 500
#debug:  capabilities:
#debug:   INVERSION_AUTO
#debug:   FEC_1_2
#debug:   FEC_2_3
#debug:   FEC_3_4
#debug:   FEC_5_6
#debug:   FEC_7_8
#debug:   FEC_AUTO
#debug:   QPSK
#debug: frequency 3830000 is in C-band (lower)
#debug: configuring LNB to v=13 p=0 satnum=0
#debug: tuning QPSK frontend to f=3830000 srate=1320000 inversion=-1 fec=999 rolloff=35 modulation=legacy pilot=-1
#warning: failed opening CAM device /dev/dvb/adapter5/ca0 (No such file or directory)
#debug: setting filter on PID 0
#debug: setting filter on PID 16
#debug: setting filter on PID 17
#debug: setting filter on PID 18
#debug: setting filter on PID 19
#debug: setting filter on PID 20
#error: no config file
#debug: frontend has acquired signal
#debug: frontend has acquired carrier
#warning: no lock, tuning again
#debug: frequency 3830000 is in C-band (lower)
#debug: configuring LNB to v=13 p=0 satnum=0
#debug: tuning QPSK frontend to f=3830000 srate=1320000 inversion=-1 fec=999 rolloff=35 modulation=legacy pilot=-1
#debug: frontend has acquired signal
#debug: frontend has acquired carrier
#warning: no lock, tuning again
#debug: frequency 3830000 is in C-band (lower)
#debug: configuring LNB to v=13 p=0 satnum=0
#debug: tuning QPSK frontend to f=3830000 srate=1320000 inversion=-1 fec=999 rolloff=35 modulation=legacy pilot=-1
#debug: frontend has acquired signal
#debug: frontend has acquired carrier
#warning: no lock, tuning again
#debug: frequency 3830000 is in C-band (lower)
#debug: configuring LNB to v=13 p=0 satnum=0
#debug: tuning QPSK frontend to f=3830000 srate=1320000 inversion=-1 fec=999 rolloff=35 modulation=legacy pilot=-1
#debug: frontend has acquired signal
#debug: frontend has acquired carrier
#debug: frontend has lost carrier
#debug: frontend has acquired carrier
#debug: frontend has lost carrier
#debug: frontend has acquired carrier
#debug: frontend has lost carrier
#debug: frontend has acquired carrier"""
#        proglist = parse_dvb(cmd3)
#        #print(proglist)
#        self.assertEqual(len(proglist), 0, 'Deveria estar vazio')
#        self.assertTrue(True, "TODO")
#    
#    def test_config(self):
#        from models import DVBSource, DVBDestination
#        ## Remover todos os sources
#        DVBSource.objects.all().delete()
#        source = DVBSource(name='Source 1')
#        source.save()
#        dest1 = DVBDestination(name='Dest 1',ip='224.0.0.11',port=5001,channel_program=1,channel_pid=225,source=source)
#        dest2 = DVBDestination(name='Dest 2',ip='224.0.0.12',port=5002,channel_program=2,channel_pid=225,source=source)
#        dest1.save()
#        dest2.save()
#        s = DVBSource.objects.all()
#        self.assertEqual(s[0], source, 'Deverial ser iguais')
#        source.record_config()
#        cfg_file = '/etc/dvblast/channels.d/%s.conf' %source.id
#        f = open(cfg_file,'r')
#        l1 = f.readline()
#        l2 = f.readline()
#        c1 = '%s:%d/udp 1 %d\n'%(dest1.ip,dest1.port,dest1.channel_program)
#        c2 = '%s:%d/udp 1 %d\n'%(dest2.ip,dest2.port,dest2.channel_program)
#        self.assertEqual(c1, l1, 'Configuração 1 gravada errado')
#        self.assertEqual(c2, l2, 'Configuração 2 gravada errado')
#        self.assertEqual('%s:%d/udp 1 %d\n'%(dest1.ip,dest1.port,dest1.channel_program), l1, 'Configuração 1 gravada errado')
#        self.assertEqual('%s:%d/udp 1 %d\n'%(dest2.ip,dest2.port,dest2.channel_program), l2, 'Configuração 2 gravada errado')
#        f.close()
#        
#        
#
#class TVODTest(TestCase):
#    def test_play_channel(self):
#        c = Client()
#        url = reverse('stream.views.tvod_play')
#        response = c.post(url, data={'seek':-200,'channel':3})
#        import simplejson as json
#        decoder = json.JSONDecoder()
#        objresponse = decoder.decode(response.content)
#        self.failUnlessEqual(objresponse['seek'],-200,'Deveria retornar o mesmo valor de seek')
#        #print(objresponse)
#
#
#




