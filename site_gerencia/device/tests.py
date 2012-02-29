#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
Testes unitários
"""

from django.test import TestCase
from django.conf import settings


class ConnectionTest(TestCase):
    def test_connection(self):
        from models import Server
        srv = Server()
        srv.name = 'local'
        srv.host = '127.0.0.1'
        srv.ssh_port = 22
        srv.username = 'nginx'
        #srv.password = 'iptv'
        srv.rsakey = '~/.ssh/id_rsa_test'
        srv.connect()
        ret = srv.execute('/bin/pwd')
        self.assertEqual(
            ret[0],
            '/var/lib/nginx\n',
            'O home deveria ser "/var/lib/nginx\n"'
        )

    #def test_register_server(self):
    #    from lib.ssh import Connection
    #    c = Connection('127.0.0.1',username='nginx',password='iptv')
    #    k = c.genKey()
    #    #print(k)

    def test_low_respose_command(self):
        from lib.ssh import Connection
        c = Connection('127.0.0.1',username='nginx',password='iptv')
        #stdin, stdout, stderr = c.new_execute('/var/lib/nginx/test')
        t = c.execute_with_timeout('/var/lib/nginx/test',timeout=2)
        self.assertEqual(
            'Inicio\nP1**********Fim',
            t,
            'Valor esperado diferente [%s]' % t
        )
        #sys.stderr.write(t)

    def test_scan_channel(self):
        from lib.ssh import Connection
        import sys
        c = Connection('172.17.0.2',
            username='helber',
            private_key='~/.ssh/id_rsa_cianet')
        r = c.execute_with_timeout('/usr/bin/dvblast -a 2 -f 3642000 -s 4370000',10)
        sys.stderr.write(r)

    #def test_control_dvb(self):
    #    self.assertFalse(False, 'Criar o controle de processos do dvb')
    #
    #def test_control_multicat(self):
    #    self.assertFalse(False, 'Criar o controle de processos do multicat')
    #
    #def test_remote_process(self):
    #    pass


class ProcessControlTest(TestCase):

    def setUp(self):
        from models import Server
        self.s = Server(
            name='local',
            host='127.0.0.1',
            ssh_port=22,
            username='nginx',
            rsakey='~/.ssh/id_rsa_test'
        )

    def test_prepare_daemon(self):
        import os
        import datetime
        cmd = '/usr/bin/cvlc -I dummy -v -R \
/mnt/projetos/gerais/videos/NovosOriginais/red_ridding_hood_4M.ts \
--sout "#std{access=udp,mux=ts,dst=192.168.0.244:5000}"'
        uid = datetime.datetime.now().toordinal()
        parsed = os.path.basename(cmd.split()[0])
        self.assertEqual(parsed, 'cvlc', 'Deveria ser retornado o comando')
        fullcmd = '/usr/sbin/daemonize -p ~/%s-%s.pid %s' %(parsed,uid,cmd)

    def test_list_process(self):
        self.s.connect()
        procs = self.s.list_process()
        self.assertEqual(procs[0]['pid'],
            1,
            'O primero processo deveria ter pid=1')

    def test_start_process(self):
        cmd = '/usr/bin/nvlc -I dummy -v -R \
/mnt/projetos/gerais/videos/NovosOriginais/red_ridding_hood_4M.ts \
--sout "#std{access=udp,mux=ts,dst=127.0.0.1:5000}"'
        pid = self.s.execute_daemon(cmd)
        self.assertGreater(pid, 0, 'O processo deveria ser maios que zero')
        self.s.kill_process(pid)
        self.assertFalse(self.s.process_alive(pid),
            'O processo pid=%d deveria ter morrido.' % pid )

