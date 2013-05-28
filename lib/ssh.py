#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""Friendly Python SSH2 interface."""

import os
import logging
import paramiko
import time


class Connection(object):
    """Connects and logs into the specified hostname.
    Arguments that are not given are guessed from the environment."""

    def __init__(self,
                 host,
                 username=None,
                 private_key=None,
                 password=None,
                 port=22,
                 ):
        log = logging.getLogger('device.remotecall')
        self._sftp_live = False
        self._sftp = None
        self._transport_live = False
        if not username:
            username = os.environ['LOGNAME']

        # Begin the SSH transport.
        self._transport = paramiko.Transport((host, port))
        # self._transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._transport_live = True
        # Authenticate the transport.
        if password:
            # Using Password.
            log.info('Connection using password')
            self._transport.connect(username=username, password=password)
        else:
            # Use Private Key.
            log.info('Connection using rsa key')
            if not private_key:
                # Try to use default key.
                if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                    private_key = '~/.ssh/id_rsa'
                elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                    private_key = '~/.ssh/id_dsa'
                else:
                    log.error('Need password or key to connect')
                    raise TypeError, "You have not specified a password or key."
            private_key_file = os.path.expanduser(private_key)
            rsa_key = paramiko.RSAKey.from_private_key_file(private_key_file)
            self._transport.connect(username=username, pkey=rsa_key)

    def _sftp_connect(self):
        """Establish the SFTP connection."""
        log = logging.getLogger('device.remotecall')
        log.info('Connecting using SFTP')
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def get(self, remotepath, localpath=None):
        """Copies a file between the remote host and the local host."""
        log = logging.getLogger('device.remotecall')
        log.info('geting file from remote:%s -> %s', remotepath, localpath)
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        self._sftp.get(remotepath, localpath)

    def put(self, localpath, remotepath=None):
        """Copies a file between the local host and the remote host."""
        log = logging.getLogger('device.remotecall')
        log.info('sending file from local:%s -> %s', localpath, remotepath)
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        self._sftp_connect()
        self._sftp.put(localpath, remotepath)

    def execute(self, command):
        """Execute the given commands on a remote machine."""
        log = logging.getLogger('device.remotecall')
        ret = {}
        channel = self._transport.open_session()
        #channel.get_pty()
        channel.exec_command(command)
        ret_code = channel.recv_exit_status()
        log.info('Return status [%s] command:%s', ret_code, command)
        ret['exit_code'] = ret_code
        output = channel.makefile('rb', -1).readlines()
        if output:
            ret['output'] = map(lambda x: unicode(x, 'utf-8'), output)
        else:
            ret['output'] = map(lambda x: unicode(x, 'utf-8'),
                channel.makefile_stderr('rb', -1).readlines())
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
        if len(output['output']):
            pid = int(output['output'][0].strip())
            log.info('Daemon started with pid [%d] command:%s', pid, fullcommand)
            ret['pid'] = pid
        return ret

    def execute_with_timeout(self, command, timeout=10):
        """
        Executa comando no servidor com timeout e retorna o stdout concatenado
        com o stderr

        Estudar e possibilidade para melhorar a conexão:
        EPoll:
        http://scotdoyle.com/python-epoll-howto.html
        Select:
        http://www.doughellmann.com/PyMOTW/select/
        twisted:
        http://twistedmatrix.com/trac/
        """
        import socket
        import select
        import time
        log = logging.getLogger('device.remotecall')
        start = time.time()
        channel = self._transport.open_session()
        channel.settimeout(timeout)
        channel.exec_command(command)
        resp = ''
        linha = ''
        run = True
        while run:
            try:
                r, w, e = select.select([channel], [], [], timeout)
                if len(r) > 0:
                    if channel.recv_ready():
                        linha = r[0].recv(1024)
                    elif channel.recv_stderr_ready():
                        linha = r[0].recv_stderr(1024)
                    else:
                        r[0].send_ready()
                        r[0].recv(1)
                if len(e) > 0:
                    channel.close()
                    run = False
                    break
                if len(w) > 0:
                    pass
                if time.time() - start > timeout:
                    channel.send_exit_status(15)
                    kcommand = "/bin/kill `ps axw | grep '%s' | grep -v grep | awk '{print $1}'`"
                    try:
                        channel.get_transport().open_session().exec_command(\
                            kcommand % (command)
                        )
                    except Exception as e:
                        log.error('Execption on kill:%s', e)
                    channel.close()
                    run = False
                    break
            except KeyboardInterrupt as e:
                channel.send_exit_status(9)
                channel.close()
                run = False
                log.error('KeyboardInterrupt:%s', e)
                break
            except socket.timeout as e:
                channel.close()
                run = False
                log.error('Socket timeout:%s', e)
                break
            if linha:
                resp += linha
                linha = ''
        return resp

    def close(self):
        """Closes the connection and cleans up."""
        log = logging.getLogger('device.remotecall')
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
            log.debug('close sftp')
        # Close the SSH Transport.
        if self._transport_live:
            self._transport.close()
            self._transport_live = False
            log.debug('close ssh')

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        log = logging.getLogger('device.remotecall')
        log.debug('__DEL__')
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
