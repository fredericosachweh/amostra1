#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Modulo: 
"""
__author__ = 'Sergio Cioban Filho'
__version__ = '1.0'
__date__ = '23/11/2012 10:23:03 AM'

import netsnmp
import sys

community = 'mmmcast'
ver = 2
port = 161

def __snmpget(community=None, host=None, port=0, oid=None):
    if community is None or host is None or oid is None or port == 0:
        return None

    bind1 = netsnmp.Varbind(oid)
    snmpget = netsnmp.snmpget(bind1,
        Version = 2,
        RemotePort=port,
        DestHost=host,
        Community=community,
        Timeout=1000000,
        Retries=1
    )
    return snmpget


def get_dvb_info(mac=None, name=None, snmpagent_ip=None):
    if mac is None and name is None:
        return None
    if snmpagent_ip is None:
        return None

    # DVB Number
    dvb_num = __snmpget(community,
        snmpagent_ip, port,
        '.1.3.6.1.4.1.1726.5.1.1.0')[0]

    if dvb_num is None:
        return None

    dvb_info = None
    dvb_num = int(dvb_num)
    for DVB_ID in range(1, dvb_num + 1):
        if (mac is None) and (name is not None):
            #dvbDescr
            oid = ".1.3.6.1.4.1.1726.5.1.2.1.2.%d" % DVB_ID
            dvb_name = __snmpget(community, snmpagent_ip, port, oid)[0]

            if (name != dvb_name) and mac is None:
                continue

        elif (mac is not None) and (name is None):
            oid = ".1.3.6.1.4.1.1726.5.1.2.1.3.%d" % DVB_ID
            dvb_mac = __snmpget(community, snmpagent_ip, port, oid)[0]

            if mac != dvb_mac:
                continue
        else:
            continue

        oid = ".1.3.6.1.4.1.1726.5.1.2.1.4.%d" % DVB_ID
        dvb_status = __snmpget(community, snmpagent_ip, port, oid)[0]

        oid = ".1.3.6.1.4.1.1726.5.1.2.1.5.%d" % DVB_ID
        dvb_strength = __snmpget(community, snmpagent_ip, port, oid)[0]

        oid = ".1.3.6.1.4.1.1726.5.1.2.1.6.%d" % DVB_ID
        dvb_snr = __snmpget(community, snmpagent_ip, port, oid)[0]

        oid = ".1.3.6.1.4.1.1726.5.1.2.1.7.%d" % DVB_ID
        dvb_ber = __snmpget(community, snmpagent_ip, port, oid)[0]

        dvb_info = "dvb_status:[%s] dvb_strength:[%s] dvb_snr:[%s] dvb_ber:[%s]" % (
            dvb_status, dvb_strength, dvb_snr, dvb_ber)
        break

    return dvb_info

def get_mcast_info(ip=None, port=None, snmpagent_ip=None):
    if ip is None or port is None or snmpagent_ip is None:
        return None

    # MULTICAST Number: .1.3.6.1.4.1.1726.5.2.1.0
    mcast_num = __snmpget(community,
        snmpagent_ip, port,
        '.1.3.6.1.4.1.1726.5.2.1.0')[0]

    if mcast_num is None:
        return None

    mcast_info = None
    mcast_num = int(mcast_num)
    for MCAST_ID in range(1, mcast_num + 1):
        #mcastIp .1.3.6.1.4.1.1726.5.2.2.1.2.
        oid = ".1.3.6.1.4.1.1726.5.2.2.1.2.%d" % MCAST_ID
        mcast_ip = __snmpget(community, snmpagent_ip, port, oid)[0]

        if mcast_ip != ip:
            continue

        oid = ".1.3.6.1.4.1.1726.5.2.2.1.3.%d" % MCAST_ID
        mcast_port = __snmpget(community, snmpagent_ip, port, oid)[0]

        if mcast_port != str(port):
            continue

        oid = ".1.3.6.1.4.1.1726.5.2.2.1.4.%d" % MCAST_ID
        mcast_type = __snmpget(community, snmpagent_ip, port, oid)[0]

        oid = ".1.3.6.1.4.1.1726.5.2.2.1.5.%d" % MCAST_ID
        mcast_bcount = __snmpget(community, snmpagent_ip, port, oid)[0]

        oid = ".1.3.6.1.4.1.1726.5.2.2.1.6.%d" % MCAST_ID
        mcast_pcount = __snmpget(community, snmpagent_ip, port, oid)[0]

        mcast_info = "type:[%s] Bytes:[%s] Pkts:[%s]" % (
            mcast_type, mcast_bcount, mcast_pcount)
        break

    return mcast_info


if __name__ == '__main__':
    print get_dvb_info(name='adapter0', snmpagent_ip='172.17.0.2')
