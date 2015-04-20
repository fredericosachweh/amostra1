#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import division, unicode_literals
import logging
from suds.client import Client
from suds import WebFault
import urllib2

log = logging.getLogger('omi')


class deviceMgmtService:

    url = None
    Device = None

    def __init__(self):
        self.url = 'https://vcas.iptvdomain:8090/services/DeviceMgmtService?wsdl'
        self.Device = Client(self.url, location='https://vcas.iptvdomain:8090/services/DeviceMgmtService')

    def add_devices(self, token, device_list):
        # addDevices(ns0:DeviceList deviceList, ns0:SessionHandle sessionHandle, )
        devices = self.Device.factory.create('ns1:DeviceList')
        for lst in device_list:
            device = self.Device.factory.create('ns1:Device')
            device.smsDeviceId = lst[0]
            device.deviceType = lst[1]
            device.smsNetworkId = lst[2]
            device.networkDeviceId = lst[3]
            devices.devices.append(device)
        try:
            print self.Device.service.addDevices(devices, token.sessionHandle)
        except WebFault, e:
            print 'Except: %s' % e

    def remove_devices(self, token, device_list):
        # removeDevices(ns0:DeviceList deviceList, ns0:SessionHandle sessionHandle, )
        devices = self.Device.factory.create('ns1:DeviceList')
        for lst in device_list:
            device = self.Device.factory.create('ns1:Device')
            device.smsDeviceId = lst[0]
            device.deviceType = lst[1]
            device.smsNetworkId = lst[2]
            device.networkDeviceId = lst[3]
            devices.devices.append(device)
        try:
            print self.Device.service.removeDevices(devices, token.sessionHandle)
        except WebFault, e:
            print 'Except: %s' % e


class adminMgmtService:

    url = None
    Admin = None

    def __init__(self):
        self.url = 'https://vcas.iptvdomain:8090/services/AdminMgmtService?wsdl'
        self.Admin = Client(self.url, location='https://vcas.iptvdomain:8090/services/AdminMgmtService')

    def login(self, user, passwd):
        # Login Admin OMI Service
        auth = self.Admin.factory.create('ns1:UserLoginAttributes')
        auth.userName = user
        auth.password = passwd

        token = self.Admin.factory.create('ns1:SessionHandle')
        token = self.Admin.service.signOn(auth)

        return token

    def logout(self, token):
        # Logout Admin OMI Service
        self.Admin.service.signOff(token.sessionHandle)


class realTimeEncryptionService:

    url = None
    RTES = None

    def __init__(self):
        self.url = 'https://vcas.iptvdomain:8090/services/AdminMgmtService?wsdl'
        self.Admin = Client(self.url, location='https://vcas.iptvdomain:8090/services/AdminMgmtService')
        self.url_content = 'https://vcas.iptvdomain:8090/services/ContentMgmtService?wsdl'
        self.Content = Client(self.url_content, location='https://vcas.iptvdomain:8090/services/ContentMgmtService')

    def create_stream(self, token, rtes_name, chNumber, in_addr, in_port, out_addr, out_port, network_id):
        # createStream(ns0:streamAttributes streamSettings, xs:string handle, )

        content = contentMgmtService()
        content_list = []
        content_tupla = (chNumber, 'Canal linear criptografado')
        content_list.append(content_tupla)
        content.add_content(token, content_list)

        smsNetworkId = network_id
        smsContentId = chNumber
        networkContentId = chNumber

        inputURL = 'udp://' + str(in_addr) + ':' + str(in_port)
        outputURL = 'udp://' + str(out_addr) + ':' + str(out_port)
        handle = token.sessionHandle.handle

        data = "<?xml version=\"1.0\"?> \
            <env:Envelope xmlns:env=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"> \
            <env:Header/> \
            <env:Body> \
            <n1:addContentToNetwork xmlns:n1=\"http://www.verimatrix.com/omi\"> \
            <networkContent xmlns:n2=\"http://www.verimatrix.com/schemas/OMItypes.xsd\"> \
            <n2:smsNetworkId>" + str(smsNetworkId) + "</n2:smsNetworkId> \
            <n2:smsContentId>" + str(smsContentId) + "</n2:smsContentId> \
            <n2:networkContentId>" + str(networkContentId) + "</n2:networkContentId> \
            <n2:networkContentType>DTV</n2:networkContentType> \
            <n2:ratingLevel>1</n2:ratingLevel> \
            <n2:encryptionAttributes> \
            <n2:dtvEncryptionAttributes xmlns:n3=\"http://www.verimatrix.com/schemas/IPTVtypes.xsd\"> \
            <n3:applianceName>" + str(rtes_name) + "</n3:applianceName> \
            <n3:inputURL>" + str(inputURL) + "</n3:inputURL> \
            <n3:outputURL>" + str(outputURL) + "</n3:outputURL> \
            <n3:copyControlAttributes> \
            <n3:ccCGMS_A>0</n3:ccCGMS_A> \
            <n3:ccACP>0</n3:ccACP> \
            <n3:ccDwightCavendish>false</n3:ccDwightCavendish> \
            <n3:ccHDCP>false</n3:ccHDCP> \
            </n3:copyControlAttributes> \
            <n3:osdAttributes> \
            <n3:osdActive>false</n3:osdActive> \
            <n3:osdDuration>0</n3:osdDuration> \
            <n3:osdType>0</n3:osdType> \
            <n3:osdLocation>0</n3:osdLocation> \
            </n3:osdAttributes> \
            <n3:encryptionAttributes> \
            <n3:description>OMI Channel Create</n3:description> \
            <n3:encryptionMode>AES</n3:encryptionMode> \
            <n3:pcrCorrection>false</n3:pcrCorrection> \
            <n3:keyMutationInterval>10000</n3:keyMutationInterval> \
            <n3:keyInsertionInterval>1000</n3:keyInsertionInterval> \
            <n3:videoMark>false</n3:videoMark> \
            <n3:controlWordPathProtection>false</n3:controlWordPathProtection> \
            <n3:videoEncryptionLevel>100</n3:videoEncryptionLevel> \
            <n3:audioEncryptionLevel>100</n3:audioEncryptionLevel> \
            </n3:encryptionAttributes> \
            </n2:dtvEncryptionAttributes> \
            </n2:encryptionAttributes> \
            </networkContent> \
            <sessionHandle xmlns:n4=\"http://www.verimatrix.com/schemas/OMItypes.xsd\"> \
            <n4:handle>" + str(handle) + "</n4:handle> \
            </sessionHandle> \
            </n1:addContentToNetwork> \
            </env:Body> \
            </env:Envelope>"
        url = 'https://vcas.iptvdomain:8090/services/ContentMgmtService/'
        postRequest = urllib2.Request(url)
        postRequest.add_header('Content-Type', 'text/xml;charset=UTF-8')
        postRequest.add_header('Accept-Encoding', 'gzip,deflate')
        postRequest.add_header('SOAPAction', 'http://www.verimatrix.com/omi/addContentToNetwork')
        try:
            postResponse = urllib2.urlopen(postRequest, data)
            print postResponse.read()
        except urllib2.HTTPError, e:
            print e
            print urllib2.HTTPError

    def delete_stream(self, token, rtes_name, chNumber, in_addr, in_port, out_addr, out_port, network_id):
        # deleteStream(xs:int channelNumber, xs:string rtesID, xs:string handle, )
        network_content = self.Content.factory.create('ns1:NetworkContent')
        network_content.smsNetworkId = network_id
        network_content.smsContentId = chNumber
        network_content.networkContentId = chNumber
        network_content.networkContentType.set('DTV')
        print self.Content.service.removeContentFromNetwork(network_content, token.sessionHandle)

    def update_stream(self, token, rtes_name, chNumber, in_addr, in_port, out_addr, out_port):
        # updateStream(xs:int channelNumber, ns0:streamAttributes streamSettings, xs:string handle, )
        content = contentMgmtService()


class entitlementMgmtService:

    url_entitlement = None
    Entitlement = None
    url_content = None
    Content = None

    def __init__(self):
        self.url_entitlement = 'https://vcas.iptvdomain:8090/services/EntitlementMgmtService?wsdl'
        self.Entitlement = Client(self.url_entitlement, location='https://vcas.iptvdomain:8090/services/EntitlementMgmtService')
        self.url_content = 'https://vcas.iptvdomain:8090/services/ContentMgmtService?wsdl'
        self.Content = Client(self.url_content, location='https://vcas.iptvdomain:8090/services/ContentMgmtService')

    def add_entitlements(self, token, entitlement_list):
        # addEntitlements(ns1:EntitlementList entitlementList, ns1:SessionHandle sessionHandle, )
        entitlementlist = self.Entitlement.factory.create('ns1:EntitlementList')
        for lst in entitlement_list:
            entitlement = self.Entitlement.factory.create('ns1:Entitlement')
            entitlement.package.smsPackageId = lst[0][0]
            entitlement.package.description = lst[0][1]
            entitlement.smsEntitlementId = lst[1]
            #entitlement.entitledEntity.entityType = lst[2]
            entitlement.entitledEntity.entityType.set(lst[2])
            entitlement.entitledEntity.entityId = lst[3]
            entitlementlist.entitlements.append(entitlement)
        print self.Entitlement.service.addEntitlements(entitlementlist, token.sessionHandle)

    def add_events_to_package(self, token, package, event_list):
        # addEventsToPackage(ns0:Package package, ns0:EventList eventList, ns0:SessionHandle sessionHandle, )
        #import pdb; pdb.set_trace()
        pack = self.Entitlement.factory.create('ns1:Package')
        eventlist = self.Content.factory.create('ns1:EventList')
        pack.smsPackageId = package[0]
        pack.description = package[1]
        for lst in event_list:
            event = self.Content.factory.create('ns1:Event')
            event.smsEventId = lst[0]
            event.smsContentId = lst[1]
            event.smsNetworkId = int(lst[2])
            eventlist.events.append(event)
        print self.Entitlement.service.addEventsToPackage(pack, eventlist, token.sessionHandle)

    def add_packages(self, token, package_list):
        # addPackages(ns0:PackageList packageList, ns1:SessionHandle sessionHandle, )
        #import pdb; pdb.set_trace()
        packageslist = self.Entitlement.factory.create('ns1:PackageList')
        for lst in package_list:
            package = self.Entitlement.factory.create('ns1:Package')
            package.smsPackageId = lst[0]
            package.description = lst[1]
            packageslist.packages.append(package)
        print self.Entitlement.service.addPackages(packageslist, token.sessionHandle)

    def get_package_events(self, token, package_id):
        # getPackageEvents(ns0:PackageEventQuery packageEventQuery, ns1:SessionHandle sessionHandle, )
        package_event_query = self.Content.factory.create('ns1:PackageEventQuery')
        package_event_query.smsPackageId = package_id
        print self.Entitlement.service.getPackageEvents(package_event_query, token.sessionHandle)

    def get_package_list(self, token, package_id):
        # getPackageList(ns0:PackageListQuery packageListQuery, ns1:SessionHandle sessionHandle, )
        package_list_query = self.Content.factory.create('ns1:PackageListQuery')
        package_list_query.smsPackageId = package_id
        package_list_query.packageCount = 10
        print self.Entitlement.service.getPackageList(package_list_query, token.sessionHandle)

    def remove_entitlements(self, token, entitlement_list):
        # removeEntitlements(ns1:EntitlementList entitlementList, ns1:SessionHandle sessionHandle, )
        entitlementlist = self.Entitlement.factory.create('ns1:EntitlementList')
        for lst in entitlement_list:
            entitlement = self.Entitlement.factory.create('ns1:Entitlement')
            entitlement.package.smsPackageId = lst[0][0]
            entitlement.package.description = lst[0][1]
            entitlement.smsEntitlementId = lst[1]
            #entitlement.entitledEntity.entityType = lst[2]
            entitlement.entitledEntity.entityType.set(lst[2])
            entitlement.entitledEntity.entityId = lst[3]
            entitlementlist.entitlements.append(entitlement)
        print self.Entitlement.service.removeEntitlements(entitlementlist, token.sessionHandle)

    def remove_events_from_package(self, token, package, event_list):
        # removeEventsFromPackage(ns0:Package package, ns0:EventList eventList, ns0:SessionHandle sessionHandle, )
        #import pdb; pdb.set_trace()
        pack = self.Entitlement.factory.create('ns1:Package')
        eventlist = self.Content.factory.create('ns1:EventList')
        pack.smsPackageId = package[0]
        pack.description = package[1]
        for lst in event_list:
            event = self.Content.factory.create('ns1:Event')
            event.smsEventId = lst[0]
            event.smsContentId = lst[1]
            event.smsNetworkId = lst[2]
            eventlist.events.append(event)
        print self.Entitlement.service.removeEventsFromPackage(pack, eventlist, token.sessionHandle)

    def remove_packages(self, token, package_list):
        # removePackages(ns0:PackageList packageList, ns0:SessionHandle sessionHandle, )
        packageslist = self.Entitlement.factory.create('ns1:PackageList')
        for lst in package_list:
            package = self.Entitlement.factory.create('ns1:Package')
            package.smsPackageId = lst[0]
            package.description = lst[1]
            packageslist.packages.append(package)
        print self.Entitlement.service.removePackages(packageslist, token.sessionHandle)


class configurationMgmtService:

    url = None
    Configuration = None

    def __init__(self):
        self.url = 'https://vcas.iptvdomain:8090/services/ConfigurationMgmtService?wsdl'
        self.Configuration = Client(self.url, location='https://vcas.iptvdomain:8090/services/ConfigurationMgmtService')

    def add_network(self, token, sms_network_id, network_type, uri):
        # addNetwork(ns1:Network network, ns1:SessionHandle sessionHandle, )
        network = self.Configuration.factory.create('ns1:Network')
        network.smsNetworkId = sms_network_id
        network.networkType = network_type
        network.connection.uri = uri
        print self.Configuration.service.addNetwork(network, token.sessionHandle)

    def get_network_list(self, token):
        # getNetworkList(ns0:SessionHandle sessionHandle, )
        return self.Configuration.service.getNetworkList(token.sessionHandle)

    def modify_network(self, token, sms_network_id, network_type, uri):
        # modifyNetwork(ns1:Network network, ns1:SessionHandle sessionHandle, )
        network = self.Configuration.factory.create('ns1:Network')
        network.smsNetworkId = sms_network_id
        network.networkType = network_type
        network.connection.uri = uri
        print self.Configuration.service.modifyNetwork(network, token.sessionHandle)

    def remove_network(self, token, sms_network_id, network_type, uri):
        # removeNetwork(ns1:Network network, ns1:SessionHandle sessionHandle, )
        network = self.Configuration.factory.create('ns1:Network')
        network.smsNetworkId = sms_network_id
        network.networkType = network_type
        network.connection.uri = uri
        print self.Configuration.service.removeNetwork(network, token.sessionHandle)


class contentMgmtService:

    url = None
    Content = None

    def __init__(self):
        self.url = 'https://vcas.iptvdomain:8090/services/ContentMgmtService?wsdl'
        self.Content = Client(self.url, location='https://vcas.iptvdomain:8090/services/ContentMgmtService')

    def add_content(self, token, content_list):
        #import pdb; pdb.set_trace()
        # Adicionando um canal linear / VoD
        # addContent(ns0:ContentList contentList, ns0:SessionHandle sessionHandle, )
        contentlist = self.Content.factory.create('ns1:ContentList')
        for lst in content_list:
            content = self.Content.factory.create('ns1:Content')
            content.smsContentId = lst[0]
            content.description = lst[1]
            contentlist.content.append(content)
        print self.Content.service.addContent(contentlist, token.sessionHandle)

    def add_content_to_network(self, token, content_to_network_list):
        # Adicionando um canal linear / VoD a Rede.
        # addContentToNetwork(ns0:NetworkContent networkContent, ns0:SessionHandle sessionHandle, )
        for lst in content_to_network_list:
            networkcontent = self.Content.factory.create('ns1:NetworkContent')
            networkcontent.smsNetworkId = lst[0]
            networkcontent.smsContentId = lst[1]
            networkcontent.networkContentId = lst[2]
            networkcontent.networkContentType = lst[3]
        print self.Content.service.addContentToNetwork(networkcontent, token.sessionHandle)

    def add_events(self, token, event_list):
        # Adicionando conteudo a evento
        # addEvents(ns0:EventList eventList, ns0:SessionHandle sessionHandle, )
        #import pdb; pdb.set_trace()
        eventlist = self.Content.factory.create('ns1:EventList')
        for lst in event_list:
            event = self.Content.factory.create('ns1:Event')
            event.smsEventId = lst[0]
            event.smsContentId = lst[1]
            event.smsNetworkId = int(lst[2])
            eventlist.events.append(event)
        print self.Content.service.addEvents(eventlist, token.sessionHandle)

    def get_content_events(self, token, content_id, event_id):
        # getContentEvents(ns0:ContentEventQuery contentEventQuery, ns0:SessionHandle sessionHandle, )
        content_event_query = self.Content.factory.create('ns1:ContentEventQuery')
        content_event_query.smsContentId = content_id
        content_event_query.smsEventId = event_id
        content_event_query.eventCount = 10
        print self.Content.service.getContentEvents(content_event_query, token.sessionHandle)

    def remove_content(self, token, content_list):
        # removeContent(ns0:ContentList contentList, ns0:SessionHandle sessionHandle, )
        contentlist = self.Content.factory.create('ns1:ContentList')
        for lst in content_list:
            content = self.Content.factory.create('ns1:Content')
            content.smsContentId = lst[0]
            content.description = lst[1]
            contentlist.content.append(content)
        print self.Content.service.removeContent(contentlist, token.sessionHandle)

    def remove_content_from_network(self, token, content_to_network_list):
        # removeContentFromNetwork(ns0:NetworkContent networkContent, ns0:SessionHandle sessionHandle, )
        #import pdb; pdb.set_trace()
        for lst in content_to_network_list:
            networkcontent = self.Content.factory.create('ns1:NetworkContent')
            networkcontent.smsNetworkId = lst[0]
            networkcontent.smsContentId = lst[1]
            networkcontent.networkContentId = lst[2]
            networkcontent.networkContentType = lst[3]
        print self.Content.service.removeContentFromNetwork(networkcontent, token.sessionHandle)

    def remove_events(self, token, event_list):
        # removeEvents(ns0:EventList eventList, ns0:SessionHandle sessionHandle, )
        eventlist = self.Content.factory.create('ns1:EventList')
        for lst in event_list:
            event = self.Content.factory.create('ns1:Event')
            event.smsEventId = lst[0]
            event.smsContentId = lst[1]
            event.smsNetworkId = lst[2]
            eventlist.events.append(event)
        print self.Content.service.removeEvents(eventlist, token.sessionHandle)

