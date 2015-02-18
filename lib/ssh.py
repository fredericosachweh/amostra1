#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""Friendly Python SSH2 interface."""
from __future__ import unicode_literals
import os
import logging
import paramiko
import time
import subprocess
import shlex


def connect(host,
            username=None,
            private_key=None,
            password=None,
            port=22,
            ):
        log = logging.getLogger('device.remotecall')
        if not username:
            username = os.environ['LOGNAME']
        cmd = "ssh %s@%s" % (username, host)

        # Complete command according to variables received
        if password:
            # Using Password.
            log.info('Connection using password')
            cmd += ' -P %s' % (password)
        elif private_key:
            # Use Private Key.
            log.info('Connection using rsa key')
            cmd += ' -i %s' % (private_key)
        else:
            log.error('Need password or key to connect')
            raise "You have not specified a password or key."

        # Spawn new connection
        log.debug('Connecting ssh using %s', cmd)
        try:
            null = open('/dev/null', 'w')
            subprocess.call(shlex.split(cmd), stdin=subprocess.PIPE, stdout=null, stderr=null)
            null.close()
        except:
            log.debug('Disconneting ssh from %s', cmd)

def _sftp_connect(self):
        """Establish the SFTP connection."""
        log = logging.getLogger('device.remotecall')
        log.info('Connecting using SFTP')
        #if not self._sftp_live:
        #    self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        #    self._sftp_live = True

def get(self, remotepath, localpath=None):
        """Copies a file between the remote host and the local host."""
        log = logging.getLogger('device.remotecall')
        log.info('geting file from remote:%s -> %s', remotepath, localpath)
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        self._sftp.get(remotepath, localpath)

def put(host, username, localpath, remotepath=None):
        """Copies a file between the local host and the remote host."""
        log = logging.getLogger('device.remotecall')
        log.info('sending file from local:%s -> %s', localpath, remotepath)
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        ret = {}
        cmd = 'scp '+localpath+' '+username+'@'+host+':'+remotepath
        try:        
            ret['output'] = subprocess.check_output(shlex.split(cmd))
            ret['exit_code'] = 0
        except subprocess.CalledProcessError as e:
            ret['output'] = e.output
            ret['exit_code'] = e.returncode
        ret['output'] = map(lambda x: unicode(x, 'utf-8'), ret['output'])              
        log.info('Return status [%s] command:%s', ret['exit_code'], cmd)
 


def execute(host, username, command):
        """Execute the given commands on a remote machine."""
        log = logging.getLogger('device.remotecall')
        ret = {}
        cmd = 'ssh '+username+'@'+host+' \"'+command+'\"'
        try:        
            ret['output'] = subprocess.check_output(shlex.split(cmd))
            ret['exit_code'] = 0
        except subprocess.CalledProcessError as e:
            ret['output'] = e.output
            ret['exit_code'] = e.returncode
        #ret['output'] = map(lambda x: unicode(x, 'utf-8'), ret['output'])
        ret['output'] = ret['output'].encode('utf-8')
        log.info('Batman returns %s', ret)
        log.info('Return status [%s] command:%s', ret['exit_code'], command)

        return ret

def execute_daemon(self, command, log_path=None):
        """
        Executa o comando em daemon e retorna o pid do processo
        Ex.:
            /usr/sbin/daemonize -p
            /home/helber/vlc.pid -o
            /home/helber/vlc.o -e
            /home/helber/vlc.e
            /usr/bin/cvlc -I dummy -v -R
            /home/videos/Novos/red_ridding_hood_4M.ts
            --sout "#std{access=udp,mux=ts,dst=192.168.0.244:5000}"
        """
        log = logging.getLogger('device.remotecall')
        ret = self.execute('/bin/mktemp')
        pidfile_path = ret['output'][0].strip()
        fullcommand = '/usr/sbin/daemonize -p %s ' % pidfile_path
        if log_path:
            fullcommand += '-o %s.out -e %s.err ' % (log_path, log_path)
        fullcommand += '%s' % command.strip()
        ret = self.execute(fullcommand)
        pidcommand = "/bin/cat %s" % pidfile_path
        # # Buscando o pid
        output = self.execute(pidcommand)
        ## unlink pidfile
        unlink_cmd = '/usr/bin/unlink %s' % pidfile_path
        log.debug('Clean pid file:%s', unlink_cmd)
        self.execute(unlink_cmd)
        if len(output['output']):
            pid = int(output['output'][0].strip())
            log.info('Daemon started with pid [%d] command:%s', pid,
                fullcommand)
            ret['pid'] = pid
        return ret

def close(self):
        """Closes the connection and cleans up."""
        if logging is not None:
            log = logging.getLogger('device.remotecall')
        # Close SFTP Connection.
        #if self._sftp_live:
        #    self._sftp.close()
        #    self._sftp_live = False
        #    if logging is not None:
        #        log.debug('close sftp')
        # Close the SSH Transport.
        #if self._transport_live:
        #    self._transport.close()
        #    self._transport_live = False
        #    if logging is not None:
        #        log.debug('close ssh')

def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        if logging is not None:
            pass
            #log = logging.getLogger('device.remotecall')
            #log.debug('__DEL__:%s', self)
        self.close()

def genKey(self):
        log = logging.getLogger('device.remotecall')
        log.debug('genKey')
        return paramiko.RSAKey.generate(2048)


def main():
    """Little test when called directly."""
    # Set these to your own details.
    myssh = Connection('example.com')
    myssh.put('ssh.py')
    myssh.close()

# start the ball rolling.
if __name__ == "__main__":
    main()
