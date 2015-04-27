#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from device.models import EncryptDeviceService
from device.models import MulticastOutput
from cas.models import RTESServer
from cas.models import Device
from cas.models import Entitlement
from cas.models import DeviceEntitlement
from cas.omi import adminMgmtService
from cas.omi import deviceMgmtService
from cas.omi import entitlementMgmtService
from cas.omi import contentMgmtService
from cas.omi import configurationMgmtService
from cas.omi import realTimeEncryptionService
from client.models import SetTopBox
from client.models import SetTopBoxChannel

import logging

log = logging.getLogger('debug')


def create_device(instance):
    devices_list = []
    admin = adminMgmtService()
    token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
    if get_network(token) < 0:
        add_network(token, get_free_network(token))
    log.debug('Creating: %s', instance)
    device = deviceMgmtService()
    device_tupla = (instance.mac.replace(':', '').upper(), 'STB_IPTV', get_network(token), instance.mac.replace(':', '').upper())
    devices_list.append(device_tupla)
    device.add_devices(token, devices_list)
    save_db_device(get_network(token), instance.mac.replace(':', '').upper())
    admin.logout(token)


def get_network(token):
    config = configurationMgmtService()
    cg = config.get_network_list(token)
    if hasattr(cg, 'networks'):
        for net_list in range(0, cg.networks.__len__()):
            if cg.networks[net_list].networkType == 'IPTV':
                return cg.networks[net_list].smsNetworkId
    return -1


def get_free_network(token):
    lst = []
    config = configurationMgmtService()
    cg = config.get_network_list(token)
    if hasattr(cg, 'networks'):
        for net_list in range(0, cg.networks.__len__()):
            lst.append(int(cg.networks[net_list].smsNetworkId))
    lst.sort()
    j = 0
    for i in lst:
        j += 1
        if i > j:
            return j
    j += 1
    return j


def add_network(token, network_id):
    config = configurationMgmtService()
    config.add_network(token, network_id, 'IPTV', 'iptv://vmx-cianet-lab:1313')


def save_db_entitlement(channel_id, ip_src, port_src, ip_dest, port_dest):
    db_entitlement = Entitlement()
    db_entitlement.channel_id = channel_id
    db_entitlement.ip_src = ip_src
    db_entitlement.port_src = port_src
    db_entitlement.ip_dest = ip_dest
    db_entitlement.port_dest = port_dest
    db_entitlement.save()


def update_db_entitlement(channel_id, ip_src, port_src, ip_dest, port_dest):
    db_entitlement = Entitlement.objects.filter(channel_id=channel_id)[0]
    db_entitlement.ip_src = ip_src
    db_entitlement.port_src = port_src
    db_entitlement.ip_dest = ip_dest
    db_entitlement.port_dest = port_dest
    db_entitlement.save()


def delete_db_entitlement(channel_id):
    Entitlement.objects.filter(channel_id=channel_id).delete()


def save_db_device(network, mac):
    db_device = Device()
    db_device.device_type = 'stb_iptv'
    db_device.network_id = network
    db_device.device_id = mac
    db_device.network_device_id = mac
    db_device.save()


def delete_db_device(mac):
    Device.objects.filter(network_device_id=mac).delete()


def save_db_deviceentitlement(stb_mac, channel_id):
    db_deviceentitlement = DeviceEntitlement()
    db_deviceentitlement.device_id = stb_mac
    db_deviceentitlement.entitlement_id = channel_id
    db_deviceentitlement.save()


def delete_db_deviceentitlement(stb_mac, channel_id):
    DeviceEntitlement.objects.filter(device_id=stb_mac, entitlement_id=channel_id).delete()


def create_entitlement(token, channel_id, network_id):
    content = contentMgmtService()
    entitlement = entitlementMgmtService()

    # create content
    # Criado previamente pelo create_stream

    # create event
    event_list = []
    event = (channel_id, channel_id, network_id)
    event_list.append(event)
    content.add_events(token, event_list)

    # create package
    package_list = []
    package = (channel_id, 'Pacote%s' % channel_id)
    package_list.append(package)
    entitlement.add_packages(token, package_list)

    # add event to package
    entitlement.add_events_to_package(token, package, event_list)


def remove_entitlement(token, channel_id, network_id):
    content = contentMgmtService()
    entitle = entitlementMgmtService()

    # remove content
    content_list = []
    content_tupla = (channel_id, 'Canal linear criptografado')
    content_list.append(content_tupla)
    content.remove_content(token, content_list)

    # remove event
    event_list = []
    event = (channel_id, channel_id, network_id)
    event_list.append(event)
    content.remove_events(token, event_list)

    # remove package
    package_list = []
    package = (channel_id, 'Pacote%s' % channel_id)
    package_list.append(package)
    entitle.remove_packages(token, package_list)

    # remove event from package
    # entitle.remove_events_from_package(token, package, event_list)

    content_to_network_list = []
    content_to_network = (network_id, channel_id, channel_id, 'DTV')
    content_to_network_list.append(content_to_network)
    content.remove_content_from_network(token, content_to_network_list)


def link_entitlement_device(token, channel_id, stb_mac):
    # import pdb; pdb.set_trace()
    entitle = entitlementMgmtService()
    entitlement_list = []
    package = (channel_id, 'Pacote%s' % channel_id)
    entitlement_id = '%sPacote%s' % (channel_id, channel_id)
    log.debug('Link Package: %s', package)
    log.debug('Link Entitlement_id: %s', entitlement_id)
    entitlement = (package, entitlement_id, 'DEVICE', stb_mac)
    entitlement_list.append(entitlement)
    entitle.add_entitlements(token, entitlement_list)

# link entitlement, package, device
# entitlements = Entitlement.factory.create('ns1:EntitlementList')
# entitlement = Entitlement.factory.create('ns1:Entitlement')
# entitlement.smsEntitlementId = 1
# entitlement.package.smsPackageId = 1
# entitlement.package.description = 1
# entitlement.entitledEntity.entityType.set('DEVICE')
# entitlement.entitledEntity.entityId = '001AD01BEF5F'
# entitlements.entitlements.append(entitlement)
# resp = Entitlement.service.addEntitlements(entitlements, token.sessionHandle)


def unlink_entitlement_device(token, channel_id, stb_mac):
    # import pdb; pdb.set_trace()
    entitle = entitlementMgmtService()
    entitlement_list = []
    package = (channel_id, 'Pacote%s' % channel_id)
    entitlement_id = '%sPacote%s' % (channel_id, channel_id)
    log.debug('UnLink Package: %s', package)
    log.debug('UnLink Entitlement_id: %s', entitlement_id)
    entitlement = (package, entitlement_id, 'DEVICE', stb_mac)
    entitlement_list.append(entitlement)
    entitle.remove_entitlements(token, entitlement_list)


@receiver(post_save, sender=MulticastOutput)
def multicast_output_post_save(sender, instance, created, **kwargs):
    if RTESServer.objects.all().exists():
        if instance.sink.content_type.name == 'Entrada CAS IPv4':
            ip = instance.ip
            dev = instance.server.get_netdev(instance.nic_sink.ipv4)
            instance.server.create_route(ip, dev)
            channel_id = instance.sink.sink.pk
            if created:
                rtes_config = RTESServer.objects.all()[0]
                rtes = realTimeEncryptionService()
                admin = adminMgmtService()
                token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
                if get_network(token) < 0:
                    add_network(token, get_free_network(token))
                rtes.create_stream(token, rtes_config.name, channel_id, instance.sink.sink.sink.ip, instance.sink.sink.sink.port, instance.ip, instance.port, get_network(token))
                create_entitlement(token, channel_id, get_network(token))
                admin.logout(token)
                save_db_entitlement(channel_id, instance.sink.sink.sink.ip, instance.sink.sink.sink.port, instance.ip, instance.port)
            else:
                pass
                # rtes_config = RTESServer.objects.all()[0]
                # rtes = realTimeEncryptionService()
                # token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
                # if get_network(token) < 0:
                #     add_network(token, get_free_network(token))
                # rtes.create_stream(token, rtes_config.name, channel_id, instance.sink.sink.sink.ip, instance.sink.sink.sink.port, instance.ip, instance.port, get_network(token))
                # create_entitlement(token, channel_id, get_network(token))
                # admin.logout(token)
                # save_db_entitlement(channel_id, instance.sink.sink.sink.ip, instance.sink.sink.sink.port, instance.ip, instance.port)


@receiver(post_delete, sender=MulticastOutput)
def multicast_output_post_delete(sender, instance, **kwargs):
    if RTESServer.objects.all().exists():
        if instance.sink.content_type.name == 'Entrada CAS IPv4':
            channel_id = instance.sink.sink.pk
            rtes_config = RTESServer.objects.all()[0]
            rtes = realTimeEncryptionService()
            admin = adminMgmtService()
            token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
            if get_network(token) < 0:
                add_network(token, get_free_network(token))
            rtes.delete_stream(token, rtes_config.name, channel_id, instance.sink.sink.sink.ip, instance.sink.sink.sink.port, instance.ip, instance.port, get_network(token))
            remove_entitlement(token, channel_id, get_network(token))
            admin.logout(token)
            delete_db_entitlement(channel_id)


@receiver(post_save, sender=EncryptDeviceService)
def encrypt_device_service_post_save(sender, instance, created, **kwargs):
    # Create a new rote
    # import pdb; pdb.set_trace()
    if RTESServer.objects.all().exists():
        ip = instance.sink.ip
        dev = instance.server.get_netdev(instance.nic_sink.ipv4)
        instance.server.create_route(ip, dev)
        # import pdb; pdb.set_trace()


@receiver(post_delete, sender=EncryptDeviceService)
def encrypt_device_service_post_delete(sender, instance, **kwargs):
    if RTESServer.objects.all().exists():
        pass


@receiver(post_save, sender=SetTopBox)
def SetTopBox_post_save(sender, instance, created, **kwargs):
    if RTESServer.objects.all().exists():
        if created:
            create_device(instance)
            # devices_list = []
            # admin = adminMgmtService()
            # token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
            # if get_network(token) < 0:
            #     add_network(token, get_free_network(token))
            # log.debug('Creating: %s', instance)
            # device = deviceMgmtService()
            # device_tupla = (instance.mac.replace(':', '').upper(), 'STB_IPTV', get_network(token), instance.mac.replace(':', '').upper())
            # devices_list.append(device_tupla)
            # device.add_devices(token, devices_list)
            # save_db_device(get_network(token), instance.mac.replace(':', '').upper())
            # admin.logout(token)


@receiver(post_delete, sender=SetTopBox)
def SetTopBox_post_delete(sender, instance, **kwargs):
    if RTESServer.objects.all().exists():
        devices_list = []
        admin = adminMgmtService()
        token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
        log.debug('Deleting: %s', instance)
        device = deviceMgmtService()
        device_tupla = (instance.mac.replace(':', '').upper(), 'STB_IPTV', '1', instance.mac.replace(':', '').upper())
        devices_list.append(device_tupla)
        device.remove_devices(token, devices_list)
        admin.logout(token)
        delete_db_device(instance.mac.replace(':', '').upper())


@receiver(post_save, sender=SetTopBoxChannel)
def SetTopBoxChannel_post_save(sender, instance, created, **kwargs):
    if RTESServer.objects.all().exists():
        # import pdb; pdb.set_trace()
        if instance.channel.sink.sink.content_type.name == 'Entrada CAS IPv4':
            if created:
                log.debug('Now we need to attache settopbox + domain with this cannel [%s]', instance)
                stb = SetTopBox.objects.filter(id=instance.settopbox_id).all()[0]
                ch = instance.channel.sink.sink.sink.pk
                admin = adminMgmtService()
                token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
                # import pdb; pdb.set_trace()
                create_device(instance.settopbox)
                link_entitlement_device(token, ch, stb.mac)
                save_db_deviceentitlement(stb.mac, ch)


@receiver(post_delete, sender=SetTopBoxChannel)
def SetTopBoxChannel_post_delete(sender, instance, **kwargs):
    if RTESServer.objects.all().exists():
        # import pdb; pdb.set_trace()
        if instance.channel.sink.content_type.name == 'Entrada CAS IPv4':
            log.debug('Now we need to detache settopbox + domain with this channel [%s]', instance)
            stb = SetTopBox.objects.filter(id=instance.settopbox_id).all()[0]
            ch = instance.channel.sink.sink.sink.pk
            admin = adminMgmtService()
            token = admin.login(RTESServer.objects.all()[0].username, RTESServer.objects.all()[0].password)
            unlink_entitlement_device(token, ch, stb.mac)
            delete_db_deviceentitlement(stb.mac, ch)

