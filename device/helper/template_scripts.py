from __future__ import unicode_literals

SYSTEMD_SLAVE_CONFIG = """
USERNAME=%(username)s
API_KEY=%(api_key)s
HOST=%(my_ip)s
PORT=%(my_port)s
COLDSTART_URL=%(coldstart_url)s
"""

SYSTEMD_COLDSTART = """\
[Unit]
Description=IPTV - kingrus - coldstart
After=network.target

[Service]
EnvironmentFile=/etc/sysconfig/iptv_slave
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/curl \
-H "Authorization: ApiKey ${USERNAME}:${API_KEY}" http://${HOST}:${PORT}${COLDSTART_URL} \
-d 'started=1'
ExecStop=/usr/bin/curl \
-H "Authorization: ApiKey ${USERNAME}:${API_KEY}" http://${HOST}:${PORT}${COLDSTART_URL} \
-d 'stoped=1'
User=nginx
Group=nginx

[Install]
WantedBy=multi-user.target\
"""


UDEV_CONF = """\
ACTION=="add",ATTRS{idVendor}=="04b4", GROUP="root", MODE="0666"
ACTION=="add",ATTRS{idVendor}=="1554", GROUP="root", MODE="0666"
ACTION=="add", SUBSYSTEM=="dvb", ENV{DVB_DEVICE_TYPE}=="frontend", RUN+="/usr/bin/curl \
-H "Authorization: ApiKey %(username)s:%(api_key)s" http://%(my_ip)s:%(my_port)s%(add_url)s \
-d 'adapter_nr=%%k'"
ACTION=="remove", SUBSYSTEM=="dvb", ENV{DVB_DEVICE_TYPE}=="frontend", RUN+="/usr/bin/curl \
-H "Authorization: ApiKey %(username)s:%(api_key)s" http://%(my_ip)s:%(my_port)s%(rm_url)s \
d 'adapter_nr=%%k'"
"""

MODPROBE_CONF = """\
blacklist dvb_usb
options dvb_usb_dw2102 debug=255 demod=0
options dvb_usb_dib0700 force_lna_activation=1
"""
