INIT_SCRIPT=u"""\
#!/bin/bash
#
# iptv_coldstart        Coldstart script for iptv project
#
# chkconfig: - 85 15
# description: The Cianet IPTV Middleware
#
### BEGIN INIT INFO
# Required-Start: $local_fs $network
# Required-Stop: $local_fs $network
# Short-Description: Send start or stop signal to middleware
# Description: This script sends a POST to the middleware 
# informing a boot or shutdown event
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

start() {
        echo -n $"Sending a server started signal... "
        /usr/bin/curl http://%(my_ip)s:%(my_port)s%(coldstart_url)s -d 'started=1'
        RETVAL=$?
        echo
        return $RETVAL
}

stop() {
        echo -n $"Sending a server stoped signal... "
        /usr/bin/curl http://%(my_ip)s:%(my_port)s%(coldstart_url)s -d 'stoped=1'
        RETVAL=$?
        echo
}

# See how we were called.
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        /usr/bin/curl http://%(my_ip)s:%(my_port)s%(status_url)s
        RETVAL=$?
        ;;
  *)
        echo $"Usage: $0 {start|stop|status}"
        RETVAL=2
esac

exit $RETVAL
"""

UDEV_CONF="""\
ACTION=="add", SUBSYSTEM=="dvb", ENV{DVB_DEVICE_TYPE}=="frontend", RUN+="/usr/bin/curl http://%(my_ip)s:%(my_port)s%(add_url)s -d 'adapter_nr=%%n'"
ACTION=="remove", SUBSYSTEM=="dvb", ENV{DVB_DEVICE_TYPE}=="frontend", RUN+="/usr/bin/curl http://%(my_ip)s:%(my_port)s%(rm_url)s -d 'adapter_nr=%%n'"
"""