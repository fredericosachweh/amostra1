#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import subprocess
import os
import signal


def list_procs():
    # ps -eo pid,comm,args
    proc = subprocess.Popen(['ps', '-eo', 'pid,comm,args'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout = proc.communicate()[0]
    ret = []
    for line in stdout.splitlines()[1:]:
        cmd = line.split()
        ret.append(
            {'pid': int(cmd[0]), 'name': cmd[1], 'command': ' '.join(cmd[2:])}
            )
    return ret


class Player(object):
    '''
    Player para controle dos servidores de canais.
    Camada do servidor para controle dos processos de multicat
    '''

    def __init__(self):
        '''
        Constructor
        '''
        from django.conf import settings
        if settings.MULTICAST_DAEMON:
            self._playerapp = settings.MULTICAST_DAEMON
        else:
            self._playerapp = 'multicat'
        self._player_name = settings.MULTICAST_APP

    def play_stream(self, stream):
        """
        Inicia um processo de multicat com o fluxo (stream)
        retorna pid
        """
        cmd = []
        cmd.append(self._playerapp)
        if stream.source.is_rtp is False:
            cmd.append('-u')
        if stream.destination.is_rtp is False:
            cmd.append('-U')
        origem = '@%s:%s' % (stream.source.ip, stream.source.port)
        destino = '%s:%s' % (stream.destination.ip, stream.destination.port)
        cmd.append(origem)
        cmd.append(destino)
        # Retorna o pid na saída padrão
        #pid = int(subprocess.check_output(cmd))
        #
        #print(cmd)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        pid = int(stdout.strip())
        proc.stdout.close()
        proc.stderr.close()

        return pid

    def stop_stream(self, stream):
        if stream.pid:
            os.kill(stream.pid, signal.SIGKILL)
        return True

    def is_playing(self, stream):
        if stream.pid:
            for p in list_procs():
                if p['pid'] == stream.pid:
                    return True
            #return psutil.pid_exists(stream.pid)
        return False

    def list_running(self):
        lista = []
        for proc in list_procs():
            if proc['name'] == self._player_name:
                lista.append(proc)
        return lista

    def kill_all(self):
        for proc in self.list_running():
            #print('kill_all:: Matando:%d'%proc['pid'])
            os.kill(proc['pid'], signal.SIGKILL)

    def direct_play(self, channel, ip, port, seek):
        ## Por hora mata o processo anterior e inicia um novo com os parametros
        for proc in self.list_running():
            if proc['command'].find(ip) > 0:
                os.kill(proc['pid'], signal.SIGKILL)
        fps = 27000000
        delta = seek * fps
        cmd = []
        cmd.append(self._playerapp)
        cmd.append('-u')
        cmd.append('-U')
        cmd.append('-k -%d' % delta)
        origem = '%s' % (channel)
        destino = '%s:%s' % (ip, port)
        cmd.append(origem)
        cmd.append(destino)
        scmd = ' '.join(cmd)
        from easyprocess import Proc
        stdout = Proc(scmd).call().stdout
        pid_ret = int(stdout.strip())
        return pid_ret

    def direct_stop(self, ip):
        ## Por hora mata o processo anterior e inicia um novo com os parametros
        for proc in self.list_running():
            if proc['command'].find(ip) > 0:
                os.kill(proc['pid'], signal.SIGKILL)

import re
r = re.compile('[0-9]{1,}')


def parse_dvb(stdout, debug=False):
    linhas = stdout.splitlines()
    res = []
    for linha in linhas:
        index = linha.find('* program number=')
        if index >= 0:
            prog, pid = r.findall(linha)
            res.append({'program': prog, 'pid': pid})
        if debug: print ('L:%s' % linha)
    return res


class DVB(object):

    def __init__(self):
        '''
        Construtor
        '''
        from django.conf import settings
        if settings.DVBLAST_APP:
            self._playerapp = settings.DVBLAST_APP
        else:
            self._playerapp = 'dvblast'
        self._player_name = settings.DVBLAST_APP


    def scan_channels(self, dvbsource):
        """
        Executa o processo de DVB para buscar os canais contidos no fluxo
        retorna a lista de canais encontrados
        """
        cmd = []
        from django.conf import settings
        dvb = settings.DVBLAST_COMMAND
        dvbsource.record_config()
        cmd.append(dvb)
        if dvbsource.hardware_id is not None:
            dev = dvbsource.get_adapter()
            if dev >= 0:
                cmd.append('-a %d'%dev)
        cmd.append('-c %s/channels.d/%s.conf' %(settings.DVBLAST_CONF_DIR,dvbsource.id))
        device = '%s'%dvbsource.device
        cmd.append(device)
        scmd = ' '.join(cmd)
        from easyprocess import Proc
        proc = Proc(scmd).call(timeout=8)
        #stdout=proc.stdout
        stdout=proc.stderr
        ret = parse_dvb(stdout,debug=True)
        if proc.is_alive():
            proc.stop()
        return ret

    def play_source(self,dvbsource):
        """
        Inicia um processo de dvblast com o fluxo (stream)
        retorna pid
        """
        cmd = []
        from django.conf import settings
        dvb = settings.DVBLAST_DAEMON
        dvbsource.record_config()
        cmd.append(dvb)
        if dvbsource.hardware_id is not None:
            dev = dvbsource.get_adapter()
            if dev >= 0:
                cmd.append('-a %d'%dev)
        cmd.append('-c %s/channels.d/%s.conf' %(settings.DVBLAST_CONF_DIR,dvbsource.id))
        device = '%s'%dvbsource.device
        cmd.append(device)
        scmd = ' '.join(cmd)
        from easyprocess import Proc
        stdout = Proc(scmd).call().stdout
        pid_ret = int(stdout.strip())
        return pid_ret

    def stop_dvb(self,dvbsource):
        """
        Interrompe a execução do processo
        """
        if dvbsource.pid:
            os.kill(dvbsource.pid,signal.SIGKILL)
        return True

    def is_playing(self,dvbsource):
        if dvbsource.pid:
            for p in list_procs():
                if p['pid'] == dvbsource.pid:
                    return True
            #return psutil.pid_exists(stream.pid)
        return False

    def list_running(self):
        lista = []
        for proc in list_procs():
            if proc['name'] == self._player_name:
                lista.append(proc)
        return lista

    def kill_all(self):
        for proc in self.list_running():
            #print('kill_all:: Matando:%d'%proc['pid'])
            os.kill(proc['pid'],signal.SIGKILL)



