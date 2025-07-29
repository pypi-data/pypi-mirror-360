import bs4
from dcim.models import *
from ipam.models import IPAddress
from tenancy.models import *
from pprint import *
from slugify import slugify, SLUG_OK
from extras.models import Tag

import hashlib
import uuid
import logging

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from extras.models import JournalEntry
from django.conf import settings

from extras.choices import JournalEntryKindChoices
from core.choices import ObjectChangeActionChoices
action_update = ObjectChangeActionChoices.ACTION_UPDATE
action_create = ObjectChangeActionChoices.ACTION_CREATE
action_delete = ObjectChangeActionChoices.ACTION_DELETE


User = get_user_model()
user = User.objects.get_or_create(username="FusionInventory")[0]
_uuid = uuid.uuid4()

# Use default Django logger. Settings are in the Django settings.
logger = logging.getLogger('django')

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["netbox_fusioninventory_plugin"]

# Map netbox object property with XML
inventory_settings = {
    "cpus": {
        "name": "xml_value(xml, 'name')",
        "manufacturer": "xml_or_unknown(xml, 'manufacturer')",
        "label": "'CPU'",
        "serial": "lazy:hashlib.md5((item['description']).encode('utf-8')).hexdigest().upper()",
        "asset_tag": "lazy:item['label'] + '-' + item['serial']",
        "tag": "{'name': 'hw:cpu', 'slug': 'hw-cpu'}",
        "description": """
'Device: ' + device['serial'] + '. ' + \
'Manufacturer: ' + xml_or_unknown(xml, 'manufacturer') + '. ' + \
'ID: ' + xml_or_unknown(xml, 'id') +  '. ' + \
'Core: ' + xml_or_unknown(xml, 'core') +  '. ' + \
'Thread: ' + xml_or_unknown(xml, 'thread') +  '. ' + \
'Model: ' + xml_or_unknown(xml, 'model') +  '. ' + \
'Speed: ' + xml_or_unknown(xml, 'speed') +  '. ' + \
'Stepping: ' + xml_or_unknown(xml, 'stepping') +  '. '
"""
    },
    "controllers": {
        "name": "xml_value(xml, 'name')",
        "manufacturer": "xml_or_unknown(xml, 'manufacturer')",
        "part_id": "xml_or_none(xml, 'productid')",
        "label": "'OTHER'",
        "serial": "lazy:hashlib.md5((item['description']).encode('utf-8')).hexdigest().upper()",
        "asset_tag": "lazy:item['label'] + '-' + item['serial']",
        "tag": "{'name': 'hw:other', 'slug': 'hw-other'}",
        "description": """
'Dev: ' + device['serial'] + '. ' + \
'Manufacturer: ' + xml_or_unknown(xml, 'manufacturer') + '. ' + \
'Product ID: ' + xml_or_unknown(xml, 'productid') + '. ' + \
'Vendor ID: ' + xml_or_unknown(xml, 'vendorid') + '. ' + \
'PCI class: ' + xml_or_unknown(xml, 'pciclass') + '. ' + \
'PCI slot: ' + xml_or_unknown(xml, 'pcislot') + '. ' + \
'PCI subsystem ID: ' + xml_or_unknown(xml, 'pcisubsystemid') + '. '
"""
    },
    # TODO: Do we need USB devices? They are temporary. And sometimes they are equal and throw a duplicate error
    # "usbdevices": {
    # },
    "memories": {
        "name": "xml_value(xml, 'caption')",
        "serial": "lazy:hashlib.md5((item['description']).encode('utf-8')).hexdigest().upper() if is_xml_value_zero(xml, 'serialnumber') else xml_value(xml, 'serialnumber').upper()",
        "manufacturer": "xml_or_unknown(xml, 'manufacturer')",
        "part_id": "xml_or_none(xml, 'model')",
        "label": "'MEMORY'",
        "asset_tag": "lazy:item['label'] +'-' + item['serial']",
        "tag": "{'name': 'hw:memory', 'slug': 'hw-memory'}",
        "description": """
'Device: ' + device['serial'] + '. ' + \
'Manufacturer: ' + xml_or_unknown(xml, 'manufacturer') + '. ' + \
'Model: ' + xml_or_unknown(xml, 'model') + '. ' + \
'Type: ' + xml_or_unknown(xml, 'type') + '. ' + \
'Speed: ' + xml_or_unknown(xml, 'speed') + '. ' + \
'Capacity: ' + xml_or_unknown(xml, 'capacity') + '. ' + \
'Slot: ' + xml_or_unknown(xml, 'numslots') + '. ' + \
'Serial: ' + xml_or_unknown(xml, 'serialnumber') + '. ' + \
'Description: ' + xml_or_unknown(xml, 'description') + '. '
"""
    },
    "monitors": {
        "name": "xml_or_unknown(xml, 'caption')",
        "manufacturer": "xml_or_unknown(xml, 'manufacturer')",
        "serial": "lazy:xml_value(xml, 'serial').upper() if (not is_xml_value_zero(xml, 'serial') and (is_xml_value_zero(xml, 'altserial') or len(xml_value(xml, 'serial')) > len(xml_value(xml, 'altserial')))) else xml_value(xml, 'altserial').upper() if (not is_xml_value_zero(xml, 'altserial')) else hashlib.md5((item['description']).encode('utf-8')).hexdigest().upper()",
        "label": "'MONITOR'",
        "asset_tag": "lazy:item['label'] +'-' + item['serial']",
        "tag": "{'name': 'hw:monitor', 'slug': 'hw-monitor'}",
        "description": """
'Device: ' + device['serial'] + '. ' + \
'Manufacturer: ' + xml_or_unknown(xml, 'manufacturer') + '. ' + \
'Serial: ' + xml_or_unknown(xml, 'serial') + '. ' + \
'Description: ' + xml_or_unknown(xml, 'description') + '. '
"""
    },
    "videos": {
        "name": "xml_value(xml, 'name')",
        "manufacturer": "xml_or_unknown(xml, 'manufacturer')",
        "label": "'GPU'",
        "serial": "lazy:hashlib.md5((item['description']).encode('utf-8')).hexdigest().upper()",
        "asset_tag": "lazy:item['label'] +'-' + item['serial']",
        "tag": "{'name': 'hw:gpu', 'slug': 'hw-gpu'}",
        "description": """
'Device: ' + device['serial'] + '. ' + \
'Manufacturer: ' + xml_or_unknown(xml, 'manufacturer') + '. ' + \
'Chipset: ' + xml_or_unknown(xml, 'chipset') + '. ' + \
'Memory: ' + xml_or_unknown(xml, 'memory') + '. ' + \
'Resolution: ' + xml_or_unknown(xml, 'resolution') + '. ' + \
'PCI slot: ' + xml_or_unknown(xml, 'pcislot') + '. '
"""
    },

    "storages": {
        "name": "xml_value(xml, 'name')",
        "manufacturer": "xml_or_unknown(xml, 'manufacturer')",
        "part_id": "xml_or_none(xml, 'model')",
        "serial": "lazy:hashlib.md5((item['description']).encode('utf-8')).hexdigest().upper() if is_xml_value_zero(xml, 'serialnumber') else xml_value(xml, 'serialnumber').upper()",
        "label": "'STORAGE'",
        "asset_tag": "lazy:item['label'] +'-' + item['serial']",
        "tag": "{'name': 'hw:storage', 'slug': 'hw-storage'}",
        "description": """
'Device: ' + device['serial'] + '. ' + \
'Manufacturer: ' + xml_or_unknown(xml, 'manufacturer') + '. ' + \
'Model: ' + xml_or_unknown(xml, 'model') + '. ' + \
'Firmware: ' + xml_or_unknown(xml, 'firmware') + '. ' + \
'Serial: ' + xml_or_unknown(xml, 'serialnumber') + '. ' + \
'Disk size: ' + xml_or_unknown(xml, 'disksize') + '. ' + \
'Interface: ' + xml_or_unknown(xml, 'interface') + '. ' + \
'Type: ' + xml_or_unknown(xml, 'type') + '. ' + \
'WWN: ' + xml_or_unknown(xml, 'wwn') + '. ' + \
'Description: ' + xml_or_unknown(xml, 'description') + '. '
"""
    },
    "networks": {
        "mac_address": "xml_or_none(xml, 'macaddr')",
        "name": "xml_value(xml, 'description')",
        "ipaddress": "xml_or_none(xml, 'ipaddress')",
        "ipmask": "xml_or_none(xml, 'ipmask')",
        "ipaddress6": "xml_or_none(xml, 'ipaddress6')",
        "ipmask6": "xml_or_none(xml, 'ipmask6')"
    }
}


def xml_value(xml, key):
    return xml.find(key).get_text(strip=True)


def xml_or_unknown(xml, key):
    return xml.find(key).get_text(strip=True) if (xml.find(key) and xml.find(key).get_text(strip=True) != '') else 'UNKNOWN'

def xmlpath_or_unknown(xml, path, key):
    # FIXME: Dirty workaround
    xml = eval('xml.' + path)
    return xml.find(key).get_text(strip=True) if (xml.find(key) and xml.find(key).get_text(strip=True) != '') else 'UNKNOWN'


def xml_or_none(xml, key):
    return xml.find(key).get_text(strip=True) if (xml.find(key) and xml.find(key).get_text(strip=True) != '') else None

def value_or_none(item, key):
    return item[key] if (key in item and item[key].strip() != '') else None


def is_xml_value_zero(xml, key):
    # FIXME: Dirty workarounds to exclude bad serials
    if (
        (not xml.find(key)) or
            (
                # Zeroes
                ((xml.find(key).get_text(strip=True)).upper().startswith('00000000') or
                (xml.find(key).get_text(strip=True)).upper().startswith('0X000000') or
                # Western Digital buggy serial
                (xml.find(key).get_text(strip=True)).upper() == 'WD' or
                # Too short serial
                len(xml.find(key).get_text(strip=True)) <= 5 or
                # Empty serial
                (xml.find(key).get_text(strip=True)) == '')
            )
        ):
        return True
    else:
        return False


def created_or_update_device(device_dict, items_array):
    related_objects = [
        "manufacturer",
        "role",
        "tenant",
        "device_type",
        "platform",
        "site",
        "location",
        "rack",
        "face",
        "virtual_chassis",
        "vc_position",
        "vc_priority",
        "cluster",
    ]
    device_update_objects = [
        "name",
        "manufacturer",
        "device_type",
        "platform",
        "serial",
        "asset_tag"
    ]

    # FIXME: Now we ignore mask
    excluded_ip_addresses = [
        "127.0.0.1"
    ]
    excluded_ip_addresses_tuple = tuple(excluded_ip_addresses)

    # FIXME: Now we ignore mask
    excluded_ip_addresses6 = [
        "fe80::1",
        "::1"
    ]
    excluded_ip_addresses6_tuple = tuple(excluded_ip_addresses6)

    # FIXME: Now we ignore mask, so use first octets
    included_ip_networks = [
        "192.168.106.",
        "192.168.108.",
        "192.168.110."
    ]
    included_ip_networks_tuple = tuple(included_ip_networks)

    # FIXME: Now we ignore mask, so use first octets
    included_ip_networks6 = [
    ]
    included_ip_networks6_tuple = tuple(included_ip_networks6)


    for key in related_objects:
        if device_dict.get(key):
            if isinstance(device_dict[key], str):
                if key == "role":
                    device_dict[key] = DeviceRole.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
                elif key == "manufacturer":
                    device_dict[key] = Manufacturer.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
                elif key == "tenant":
                    device_dict[key] = Tenant.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
                elif key == "device_type":
                    # FIXME: Will throw an error if manufacturer wasn't get_or_created() before this key
                    device_dict[key] = DeviceType.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"model": device_dict[key], "manufacturer": device_dict["manufacturer"], "slug": slugify(device_dict[key], only_ascii=True)}

                    )[0]
                    del device_dict["manufacturer"]
                elif key == "platform":
                    device_dict[key] = Platform.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
                elif key == "site":
                    device_dict[key] = Site.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
                elif key == "location":
                    device_dict[key] = Location.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
                elif key == "rack":
                    device_dict[key] = Rack.objects.get_or_create(
                        slug=slugify(device_dict[key], only_ascii=True), 
                        defaults={"name": device_dict[key], "slug": slugify(device_dict[key], only_ascii=True)}
                    )[0]
        else:
            del device_dict[key]
    to_del = []
    for k, v in device_dict.items():
        if not v:
            to_del.append(k)
    for key in to_del:
        del device_dict[key]

    journal_entries = []
    if ('serial' in device_dict):
        device_serial = device_dict['serial']
        devices = Device.objects.filter(serial=device_serial).all()
        if (devices.count() > 1):
            # TODO: We must report such devices via email
            logger.error(
                f'There are more than 1 device with this serial ({device_serial}): {devices}')
        else:
            try:
                device, device_created = Device.objects.get_or_create(
                    serial=device_dict['serial'], defaults=device_dict)
            except Exception as e:
                logger.error(e)
                return

            if (device_created):
                logger.info(
                    f'Creating a new device {device.name}, serial {device.serial} ({device_dict})')
                device.save()
                log = device.to_objectchange(action_create)
                log.user = user
                log.request_id = _uuid
                log.save()
                journal_entries.append(
                    JournalEntry(
                        assigned_object=device,
                        created_by=user,
                        kind=JournalEntryKindChoices.KIND_INFO,
                        comments=f'Created a new device {device.name}, serial {device.serial}'
                    ),
                )

                # Iterate all the items from the FusionInventory

                # Collect all network interfaces:
                # 1. When the new device is being created, we just get_or_create() all IP addresses and interfaces
                # 2. In case of updating the interface we should get all already existing IP addresses/interfaces first via get()->true->update,
                #  then unassociate not existed IP addresses via get()-> true -> del from interface, but from the netbox?
                # 3. What about interfaces? How do we delete non-existent?

                # FIXME: Didn't work with nested list comprehension [ [print(v2['asset_tag']) for v2 in v1 if 'asset_tag' in v2] for v1 in items_array.values()]
                # asset_tags_list = []
                # for item1 in items_array.values():
                #     for item2 in item1:
                #         if ('asset_tag' in item2 and item2['asset_tag'] != ''):
                #             asset_tags_list.append(item2['asset_tag'])

                for key, value in items_array.items():
                    if (key == 'networks'):
                        for item in value:
                            logger.info(f'Creating network')
                            ip_address = None
                            ip_address6 = None
                            if ('ipaddress' in item and 'ipmask' in item):
                                if (not item['ipaddress'] in excluded_ip_addresses and item['ipaddress'].startswith(included_ip_networks_tuple)):
                                    try:
                                        ip_address, ip_created = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress"]}/{item["ipmask"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {item["ipaddress"]}/{item["ipmask"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created):
                                            logger.warning(
                                                f'IP address {ip_address.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress"]} due to the rules.'
                                    #     ),
                                    # )
                            elif ('ipaddress' in item):
                                if (not item['ipaddress'] in excluded_ip_addresses and item['ipaddress'].startswith(included_ip_networks_tuple)):
                                    try:
                                        ip_address, ip_created = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {item["ipaddress"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created):
                                            logger.warning(
                                                f'IP address {ip_address.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress"]} due to the rules.'
                                    #     ),
                                    # )

                            if ('ipaddress6' in item and 'ipmask6' in item):
                                if (not item['ipaddress6'] in excluded_ip_addresses6 and item['ipaddress6'].startswith(included_ip_networks6_tuple)):
                                    try:
                                        ip_address6, ip_created6 = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress6"]}/{item["ipmask6"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {item["ipaddress6"]}/{item["ipmask6"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created6):
                                            logger.warning(
                                                f'IP address {ip_address6.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress6"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress6"]} due to the rules.'
                                    #     ),
                                    # )
                            elif ('ipaddress6' in item):
                                if (not item['ipaddress6'] in excluded_ip_addresses6 and item['ipaddress6'].startswith(included_ip_networks6_tuple)):
                                    try:
                                        ip_address6, ip_created6 = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress6"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {item["ipaddress6"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created6):
                                            logger.warning(
                                                f'IP address {ip_address6.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress6"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress6"]} due to the rules.'
                                    #     ),
                                    # )

                            logger.info(f'Creating/updating interface {item}')
                            try:
                                interface, interface_created = device.interfaces.get_or_create(
                                    name=item['name'][:64])
                            except Exception as e:
                                logger.error(e)
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Interface {item["name"]} was not created/updated due to the error {e}'
                                    ),
                                )
                                continue

                            mac_address = value_or_none(item,'mac_address')

                            if (not interface_created):
                                if (interface.mac_address != mac_address):
                                    logger.warning(
                                            f'Got iface:Set a new MAC address {mac_address} to the existing interface {interface.name}')
                                    interface.snapshot()
                                    interface.mac_address = mac_address
                                    interface.save()
                                    log = interface.to_objectchange(
                                        action_update)
                                    log.user = user
                                    log.request_id = _uuid
                                    log.save()
                                    journal_entries.append(
                                        JournalEntry(
                                            assigned_object=device,
                                            created_by=user,
                                            kind=JournalEntryKindChoices.KIND_WARNING,
                                            comments=f'Set a new MAC address {mac_address} to the existing interface {interface.name}'
                                        ),
                                    )

                                if (ip_address is not None):
                                    interface.snapshot()
                                    if (ip_created):
                                        logger.info(
                                            f'Got iface:Adding a new IPv4 address {ip_address.address} to the existing interface {interface.name}')
                                    else:
                                        logger.warning(
                                            f'Got iface:Moving the already existing IPv4 address {ip_address.address} to the existing interface {interface.name}')
                                        ip_address.snapshot()
                                    try:
                                        interface.ip_addresses.add(ip_address)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {ip_address.address} was not added to the interface {interface.name} due to the error {e}'
                                            ),
                                        )
                                    else:
                                        interface.save()
                                        ip_address.save()
                                        log = interface.to_objectchange(
                                            action_update)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created):
                                            log = ip_address.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )

                                if (ip_address6 is not None):
                                    interface.snapshot()
                                    if (ip_created6):
                                        logger.info(
                                            f'Got iface:Adding a new IPv6 address {ip_address6.address} to the existing interface {interface.name}')
                                    else:
                                        logger.warning(
                                            f'Got iface:Moving the already existing IPv6 address {ip_address6.address} to the existing interface {interface.name}')
                                        ip_address6.snapshot()
                                    try:
                                        interface.ip_addresses.add(ip_address6)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {ip_address6.address} was not added to the interface {interface.name} due to the error {e}'
                                            ),
                                        )
                                    else:
                                        interface.save()
                                        ip_address6.save()
                                        log = interface.to_objectchange(
                                            action_update)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created6):
                                            log = ip_address6.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address6.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv6 address {ip_address6.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv6 address {ip_address6.address} to the existing interface {interface.name}'
                                                ),
                                            )

                            else:
                                mac_address = value_or_none(item,'mac_address')
                                interface.mac_address = mac_address
                                interface.save()

                                if (ip_address is not None):
                                    if (ip_created):
                                        logger.info(
                                            f'Adding a new IPv4 address {ip_address.address} to a new interface {interface.name}')
                                    else:
                                        logger.warning(
                                            f'Moving the already existing IPv4 address {ip_address.address} to a new interface {interface.name}')
                                        ip_address.snapshot()
                                    try:
                                        interface.ip_addresses.add(ip_address)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {ip_address.address} was not added to the interface {interface.name} due to the error {e}'
                                            ),
                                        )
                                    else:
                                        interface.save()
                                        ip_address.save()
                                        log = interface.to_objectchange(
                                            action_create)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created):
                                            log = ip_address.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )

                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )

                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )

                                if (ip_address6 is not None):
                                    if (ip_created6):
                                        logger.info(
                                            f'Adding a new IPv6 address {ip_address6.address} to a new interface {interface.name}')
                                    else:
                                        logger.warning(
                                            f'Moving the already existing IPv6 address {ip_address6.address} to a new interface {interface.name}')
                                        ip_address6.snapshot()
                                    try:
                                        interface.ip_addresses.add(ip_address6)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {ip_address6.address} was not added to the interface {interface.name} due to the error {e}'
                                            ),
                                        )
                                    else:
                                        interface.save()
                                        ip_address6.save()
                                        log = interface.to_objectchange(
                                            action_create)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created6):
                                            log = ip_address6.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address6.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )

                    else:
                        for item in value:
                            tag = None
                            tag_created = None
                            # FIXME: We do list() to avoid RuntimeError: dictionary changed size during iteration (see del() below)
                            for k, v in list(item.items()):
                                if k == "manufacturer":
                                    try:
                                        item[k] = Manufacturer.objects.get_or_create(
                                            slug=slugify(item[k], only_ascii=True), 
                                            defaults={"name": item[k], "slug": slugify(item[k], only_ascii=True)}
                                        )[0]
                                    except Exception as e:
                                        logger.error(e)
                                        continue
                                elif k == "tag":
                                    try:
                                        tag, tag_created = Tag.objects.get_or_create(
                                            name=item[k]['name'],
                                            slug=item[k]['slug'],
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        continue
                                    else:
                                        # Delete our special key, InventoryItem does not have this key in its model
                                        # FIXME: Should we delete this?
                                        del item[k]
                                elif k == "name":
                                    # Shorten string
                                    item[k] = item[k][:64]
                                elif (k == "serial" or k == "part_id" or k == "asset_tag"):
                                    # Shorten string
                                    item[k] = item[k][:50]
                                elif k == "description":
                                    # Shorten string
                                    item[k] = item[k][:200]

                            item['discovered'] = True
                            logger.info(
                                f'Creating item {item} for the device {device.name}')

                            # Continue the loop if we couldn't add an item. Report an error and add Journal entry
                            try:
                                inventory_item, item_created = InventoryItem.objects.get_or_create(
                                    asset_tag=item['asset_tag'], defaults={'device': device, **item})
                            except Exception as e:
                                logger.error(e)
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Item {item} was not added to the device {device.name} due to the error {e}'
                                    ),
                                )
                                continue

                            if (not item_created):
                                logger.warning(
                                    f'Item with the asset_tag {inventory_item.asset_tag} previously was related to the device {inventory_item.device.name}. Change its device to the {device.name}')
                                old_device = inventory_item.device
                                inventory_item.snapshot()
                                for k, v in item.items():
                                    setattr(inventory_item, k, v)
                                inventory_item.device = device
                                # Add tag. Do not skip if we could not add the tag, but report the error and add a Journal entry.
                                if (tag is not None):
                                    try:
                                        inventory_item.tags.add(tag)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'Tag {tag} was not created for the inventory item {inventory_item.name} due to the error {e}'
                                            ),
                                        )

                                inventory_item.save()
                                log = inventory_item.to_objectchange(
                                    action_update)
                                log.user = user
                                log.request_id = _uuid
                                log.save()
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Item with the asset_tag {inventory_item.asset_tag} previously was related to the device {inventory_item.device.name}. Change its device to the {device.name}'
                                    ),
                                )

                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=old_device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Item with the asset_tag {inventory_item.asset_tag} previously was related to the device {inventory_item.device.name}. Change its device to the {device.name}'
                                    ),
                                )

                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=inventory_item,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Item with the asset_tag {inventory_item.asset_tag} previously was related to the device {inventory_item.device.name}. Change its device to the {device.name}'
                                    ),
                                )

                            else:
                                # Add tag. Do not skip if we could not add the tag, but report the error and add a Journal entry.
                                if (tag is not None):
                                    try:
                                        inventory_item.tags.add(tag)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'Tag {tag} was not created for the inventory item {inventory_item.name} due to the error {e}'
                                            ),
                                        )

                                # Report about just created inventory item
                                inventory_item.save()
                                log = inventory_item.to_objectchange(
                                    action_create)
                                log.user = user
                                log.request_id = _uuid
                                log.save()
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_INFO,
                                        comments=f'Added a new inventory item {inventory_item.name} to the device {device.name}'
                                    ),
                                )
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=inventory_item,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_INFO,
                                        comments=f'Added a new inventory item {inventory_item.name} to the device {device.name}'
                                    ),
                                )

            else:
                logger.info(
                    f'Updating the existing device {device.name}, serial {device.serial} ({device_dict})')

                # Remove keys which we are not going to update
                for k in list(device_dict.keys()):
                    if (not k in device_update_objects):
                        del device_dict[k]

                device_updated = False
                device.snapshot()
                for k, v in device_dict.items():
                    if (getattr(device, k) != device_dict[k]):
                        setattr(device, k, v)
                        device_updated = True
                if (device_updated):
                    device.save()
                    log = device.to_objectchange(action_update)
                    log.user = user
                    log.request_id = _uuid
                    log.save()
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=device,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_INFO,
                            comments=f'Updated the existing device {device.name}, serial {device.serial}'
                        ),
                    )

                # Updating the items
                # FIXME: We must refactor this and merge two huge functions in a smaller one

                # Find all current items of the current device with asset_tags which do not exist in the new dataset, mark them and discovered = False and change asset_tag to 'LOST-'+asset_tag

                # FIXME: Didn't work with nested list comprehension [ [print(v2['asset_tag']) for v2 in v1 if 'asset_tag' in v2] for v1 in items_array.values()]
                asset_tags_list = []
                for item1 in items_array.values():
                    for item2 in item1:
                        if ('asset_tag' in item2 and item2['asset_tag'].strip() != ''):
                            asset_tags_list.append(item2['asset_tag'].strip())

                # FIXME: Ugly and redundant solution. As much ugly as the above solution
                # Collect all current interfaces and mark disabled those which do not exist
                # Collect all current IP-addresses and delete those which do not exist. Use lower() for addresses
                interfaces_list = []
                addresses_list = []
                if ('networks' in items_array.keys()):
                    for item1 in items_array['networks']:
                        if ('name' in item1 and item1['name'].strip() != ''):
                            interfaces_list.append(item1['name'].strip()[:64])
                        if ('ipaddress' in item1 and item1['ipaddress'].strip() != ''):
                            addresses_list.append(item1['ipaddress'].strip().lower())
                        if ('ipaddress6' in item1 and item1['ipaddress6'].strip() != ''):
                            addresses_list.append(item1['ipaddress6'].strip().lower())

                # Tuple for istartswith()
                addresses_list_tuple = tuple(addresses_list)

                # Mark as undiscovered when it's lost
                for lost_item in (InventoryItem.objects.filter(device=device).filter(discovered=True).exclude(asset_tag__in=asset_tags_list)):
                    logger.warning(
                        f'Item with the asset_tag {lost_item.asset_tag} does not exist in the new inventory data of the device {device.name}. Mark it as not discovered')
                    lost_item.snapshot()
                    lost_item.discovered = False
                    lost_item.save()
                    log = lost_item.to_objectchange(action_update)
                    log.user = user
                    log.request_id = _uuid
                    log.save()
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=device,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Item with the asset_tag {lost_item.asset_tag} does not exist in the new inventory data of the device {device.name}. Mark it as not discovered'
                        ),
                    )
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=lost_item,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Item with the asset_tag {lost_item.asset_tag} does not exist in the new inventory data of the device {device.name}. Mark it as not discovered'
                        ),
                    )

                # Mark as discovered (even if it's not marked as undiscovered) and update when it's found in our device and was related to another one.
                # Other item data will be updated later in the main loop
                for found_item in (InventoryItem.objects.filter(asset_tag__in=asset_tags_list).exclude(device=device)):
                    logger.warning(
                        f'Item with the asset_tag {found_item.asset_tag} previously was related to the device {found_item.device.name}. Mark it as discovered again and change its device to the {device.name}')
                    old_device = found_item.device
                    found_item.snapshot()
                    found_item.discovered = True
                    found_item.device = device
                    found_item.save()
                    log = found_item.to_objectchange(action_update)
                    log.user = user
                    log.request_id = _uuid
                    log.save()
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=device,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Item with the asset_tag {found_item.asset_tag} previously was related to the device {old_device.name}. Mark it as discovered again and change its device to the {device.name}'
                        ),
                    )
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=found_item,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Item with the asset_tag {found_item.asset_tag} previously was related to the device {old_device.name}. Mark it as discovered again and change its device to the {device.name}'
                        ),
                    )
                    if (old_device != device):
                        journal_entries.append(
                            JournalEntry(
                                assigned_object=old_device,
                                created_by=user,
                                kind=JournalEntryKindChoices.KIND_WARNING,
                                comments=f'Item with the asset_tag {found_item.asset_tag} previously was related to the device {old_device.name}. Mark it as discovered again and change its device to the {device.name}'
                            ),
                        )

                # Report about an item that was undiscovered in our device and now discovered again
                # Other item data will be updated later in the main loop
                for found_item in (InventoryItem.objects.filter(device=device).filter(discovered=False).filter(asset_tag__in=asset_tags_list)):
                    logger.warning(
                        f'Item with the asset_tag {found_item.asset_tag} previously was removed from the device {device.name} and now discovered back. Mark it as discovered again')
                    found_item.snapshot()
                    found_item.discovered = True
                    found_item.save()
                    log = found_item.to_objectchange(action_update)
                    log.user = user
                    log.request_id = _uuid
                    log.save()
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=device,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Item with the asset_tag {found_item.asset_tag} previously was removed from the device {device.name} and now discovered back. Mark it as discovered again'
                        ),
                    )
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=found_item,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Item with the asset_tag {found_item.asset_tag} previously was removed from the device {device.name} and now discovered back. Mark it as discovered again'
                        ),
                    )

                # Mark interfaces as disabled when it's lost
                # FIXME: We have another loop to remove the lost IP-addresses below. Beware.
                for lost_interface in (device.interfaces.filter(enabled=True).exclude(name__in=interfaces_list)):
                    logger.warning(
                        f'Interface with the name {lost_interface.name} does not exist in the new inventory data of the device {device.name}. Mark it as disabled')
                    lost_interface.snapshot()
                    lost_interface.enabled = False
                    lost_interface.save()
                    log = lost_interface.to_objectchange(action_update)
                    log.user = user
                    log.request_id = _uuid
                    log.save()
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=device,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Interface with the name {lost_interface.name} does not exist in the new inventory data of the device {device.name}. Mark it as disabled'
                        ),
                    )

                # Mark interfaces as enabled again when it's found
                for found_interface in (device.interfaces.filter(enabled=False).filter(name__in=interfaces_list)):
                    logger.warning(
                        f'Disabled interface with the name {found_interface.name} found in the new inventory data of the device {device.name}. Mark it as enabled')
                    found_interface.snapshot()
                    found_interface.enabled = True
                    found_interface.save()
                    log = found_interface.to_objectchange(action_update)
                    log.user = user
                    log.request_id = _uuid
                    log.save()
                    journal_entries.append(
                        JournalEntry(
                            assigned_object=device,
                            created_by=user,
                            kind=JournalEntryKindChoices.KIND_WARNING,
                            comments=f'Disabled interface with the name {found_interface.name} found in the new inventory data of the device {device.name}. Mark it as enabled'
                        ),
                    )

                # Remove lost IP-addresses. Take into consideration excluded addresses and included networks
                # FIXME: We do not take into consideration the mask!
                # FIXME: Looks like Django doesn't support tuples for istartswith(), so we have to iterate
                # FIXME: We already lowered tuples above
                # FIXME: BUG: will startswith(excluded_ip_addresses_tuple) match 192.168.108.8 when there is address 192.168.108.80?
                for interface in device.interfaces.all():
                    addresses_unlinked = False
                    for address in interface.ip_addresses.all():
                        if (not str(address.address.ip).lower().startswith(excluded_ip_addresses_tuple) and not str(address.address.ip).lower().startswith(excluded_ip_addresses6_tuple) and (str(address.address.ip).lower().startswith(included_ip_networks_tuple) or str(address.address.ip).lower().startswith(included_ip_networks6_tuple)) and not str(address.address.ip).lower().startswith(addresses_list_tuple)):
                            logger.warning(
                                f'IP address {address.address} does not exist in the new inventory data of the device {device.name}. Unlink it.')
                            # Make a snapshot for the first time
                            if (not addresses_unlinked):
                                interface.snapshot()
                                addresses_unlinked = True

                            address.snapshot()
                            journal_entries.append(
                                JournalEntry(
                                    assigned_object=device,
                                    created_by=user,
                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                    comments=f'IP address {address.address} does not exist in the new inventory data of the device {device.name}. Unlink it.'
                                ),                        
                            )
                            journal_entries.append(
                                JournalEntry(
                                    assigned_object=address,
                                    created_by=user,
                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                    comments=f'IP address {address.address} does not exist in the new inventory data of the device {device.name}. Unlink it.'
                                ),                        
                            )
                            # Unlink it
                            address.assigned_object_type = None
                            address.assigned_object_id = None
                            address.save()
                            
                            log = address.to_objectchange(action_update)
                            log.user = user
                            log.request_id = _uuid
                            log.save()
                    # Save and report changes
                    if (addresses_unlinked):
                        interface.save()
                        log = interface.to_objectchange(action_update)
                        log.user = user
                        log.request_id = _uuid
                        log.save()
                        # FIXME: Redundant but to be sure.
                        addresses_unlinked = False

                # FIXME: Should we run device.save() here and in all other cases above and below?
                # device.save()

                # FIXME: Mostly the same code as for creating. We must refactor this!
                for key, value in items_array.items():
                    if (key == 'networks'):
                        for item in value:
                            logger.info(f'Updating network')
                            ip_address = None
                            ip_address6 = None
                            interface_updated = False
                            if ('ipaddress' in item and 'ipmask' in item):
                                if (not item['ipaddress'] in excluded_ip_addresses and item['ipaddress'].startswith(included_ip_networks_tuple)):
                                    try:
                                        ip_address, ip_created = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress"]}/{item["ipmask"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {item["ipaddress"]}/{item["ipmask"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created):
                                            logger.info(
                                                f'IP address {ip_address.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress"]} due to the rules.'
                                    #     ),
                                    # )
                            elif ('ipaddress' in item):
                                if (not item['ipaddress'] in excluded_ip_addresses and item['ipaddress'].startswith(included_ip_networks_tuple)):
                                    try:
                                        ip_address, ip_created = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {item["ipaddress"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created):
                                            logger.info(
                                                f'IP address {ip_address.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress"]} due to the rules.'
                                    #     ),
                                    # )

                            if ('ipaddress6' in item and 'ipmask6' in item):
                                if (not item['ipaddress6'] in excluded_ip_addresses6 and item['ipaddress6'].startswith(included_ip_networks6_tuple)):
                                    try:
                                        ip_address6, ip_created6 = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress6"]}/{item["ipmask6"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {item["ipaddress6"]}/{item["ipmask6"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created6):
                                            logger.info(
                                                f'IP address {ip_address6.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress6"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress6"]} due to the rules.'
                                    #     ),
                                    # )
                            elif ('ipaddress6' in item):
                                if (not item['ipaddress6'] in excluded_ip_addresses6 and item['ipaddress6'].startswith(included_ip_networks6_tuple)):
                                    try:
                                        ip_address6, ip_created6 = IPAddress.objects.get_or_create(
                                            address=f'{item["ipaddress6"]}'
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {item["ipaddress6"]} was not created due to the error {e}'
                                            ),
                                        )
                                    else:
                                        if (not ip_created6):
                                            logger.info(
                                                f'IP address {ip_address6.address} already exists.')
                                else:
                                    logger.warning(
                                        f'Excluded an IP address {item["ipaddress6"]} due to the rules.')
                                    # journal_entries.append(
                                    #     JournalEntry(
                                    #         assigned_object=device,
                                    #         created_by=user,
                                    #         kind=JournalEntryKindChoices.KIND_WARNING,
                                    #         comments=f'Excluded an IP address {item["ipaddress6"]} due to the rules.'
                                    #     ),
                                    # )

                            logger.info(f'Updating/creating interface {item["name"]}. Received data: {item}')
                            try:
                                interface, interface_created = device.interfaces.get_or_create(
                                    name=item['name'][:64])
                            except Exception as e:
                                logger.error(e)
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Interface {item["name"]} was not created due to the error {e}'
                                    ),
                                )
                                continue

                            mac_address = value_or_none(item,'mac_address')

                            if (not interface_created):
                                if (interface.mac_address != mac_address):
                                    logger.warning(
                                            f'Got iface:Set a new MAC address {mac_address} to the existing interface {interface.name}')
                                    interface.snapshot()
                                    interface.mac_address = mac_address
                                    interface.save()
                                    log = interface.to_objectchange(
                                        action_update)
                                    log.user = user
                                    log.request_id = _uuid
                                    log.save()
                                    journal_entries.append(
                                        JournalEntry(
                                            assigned_object=device,
                                            created_by=user,
                                            kind=JournalEntryKindChoices.KIND_WARNING,
                                            comments=f'Set a new MAC address {mac_address} to the existing interface {interface.name}'
                                        ),
                                    )
                                interface.snapshot()
                                if (ip_address is not None):
                                    if (ip_created):
                                        logger.info(
                                            f'Got iface:Adding a new IPv4 address {ip_address.address} to the existing interface {interface.name}')
                                    else:
                                        logger.info(
                                            f'Got iface:Updating the already existing IPv4 address {ip_address.address} for the existing interface {interface.name}')
                                        ip_address.snapshot()

                                    if (not ip_address in interface.ip_addresses.all()):
                                        try:
                                            interface.ip_addresses.add(
                                                ip_address)
                                        except Exception as e:
                                            logger.error(e)
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'IPv4 address {ip_address.address} was not added to the interface {interface.name} due to the error {e}'
                                                ),
                                            )
                                        else:
                                            interface_updated = True

                                    if (interface_updated):
                                        interface.save()
                                        ip_address.save()
                                        log = interface.to_objectchange(
                                            action_update)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created):
                                            log = ip_address.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Updated the already existing IPv4 address {ip_address.address} for the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Updated the already existing IPv4 address {ip_address.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                    # Clear the interface_updated boolean at the end to allow next block
                                    # FIXME: May be we should use separate boolean for IPv4/IPv6?
                                    interface_updated = False

                                if (ip_address6 is not None):
                                    if (ip_created6):
                                        logger.info(
                                            f'Got iface:Adding a new IPv6 address {ip_address6.address} to the existing interface {interface.name}')
                                    else:
                                        logger.info(
                                            f'Got iface:Updating the already existing IPv6 address {ip_address6.address} for the existing interface {interface.name}')
                                        ip_address6.snapshot()

                                    if (not ip_address6 in interface.ip_addresses.all()):
                                        try:
                                            interface.ip_addresses.add(
                                                ip_address6)
                                        except Exception as e:
                                            logger.error(e)
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'IPv6 address {ip_address6.address} was not added to the interface {interface.name} due to the error {e}'
                                                ),
                                            )
                                        else:
                                            interface_updated = True

                                    if (interface_updated):
                                        interface.save()
                                        ip_address6.save()
                                        log = interface.to_objectchange(
                                            action_update)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created6):
                                            log = ip_address6.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to the existing interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address6.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Updated the already existing IPv6 address {ip_address6.address} for the existing interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Updated the already existing IPv6 address {ip_address6.address} for the existing interface {interface.name}'
                                                ),
                                            )

                            else:
                                # Interface has been just created
                                logger.info(f'Created new interface {item["name"]}')
                                mac_address = value_or_none(item,'mac_address')
                                interface.mac_address = mac_address
                                interface.save()

                                if (ip_address is not None):
                                    if (ip_created):
                                        logger.info(
                                            f'Adding a new IPv4 address {ip_address.address} to a new interface {interface.name}')
                                    else:
                                        logger.warning(
                                            f'Moving the already existing IPv4 address {ip_address.address} to a new interface {interface.name}')
                                        ip_address.snapshot()
                                    try:
                                        interface.ip_addresses.add(ip_address)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv4 address {ip_address.address} was not added to the interface {interface.name} due to the error {e}'
                                            ),
                                        )
                                    else:
                                        # Uncondidionally report, because the IP addresss was just added to the interface
                                        interface.save()
                                        ip_address.save()
                                        log = interface.to_objectchange(
                                            action_create)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created):
                                            log = ip_address.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )

                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )

                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv4 address {ip_address.address} to a new interface {interface.name}'
                                                ),
                                            )

                                if (ip_address6 is not None):
                                    if (ip_created6):
                                        logger.info(
                                            f'Adding a new IPv6 address {ip_address6.address} to a new interface {interface.name}')
                                    else:
                                        logger.warning(
                                            f'Moving the already existing IPv6 address {ip_address6.address} to a new interface {interface.name}')
                                        ip_address6.snapshot()
                                    try:
                                        interface.ip_addresses.add(ip_address6)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'IPv6 address {ip_address6.address} was not added to the interface {interface.name} due to the error {e}'
                                            ),
                                        )
                                    else:
                                        # Uncondidionally report, because the IP addresss was just added to the interface
                                        interface.save()
                                        ip_address6.save()
                                        log = interface.to_objectchange(
                                            action_create)
                                        log.user = user
                                        log.request_id = _uuid
                                        log.save()
                                        if (ip_created6):
                                            log = ip_address6.to_objectchange(
                                                action_create)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_INFO,
                                                    comments=f'Added a new IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )
                                        else:
                                            log = ip_address6.to_objectchange(
                                                action_update)
                                            log.user = user
                                            log.request_id = _uuid
                                            log.save()
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=ip_address6,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Moved the already existing IPv6 address {ip_address6.address} to a new interface {interface.name}'
                                                ),
                                            )

                    else:
                        for item in value:
                            tag = None
                            tag_created = None
                            item_updated = False
                            # FIXME: We do list() to avoid RuntimeError: dictionary changed size during iteration (see del() below)
                            for k, v in list(item.items()):
                                if k == "manufacturer":
                                    try:
                                        item[k] = Manufacturer.objects.get_or_create(
                                            slug=slugify(item[k], only_ascii=True), 
                                            defaults={"name": item[k], "slug": slugify(item[k], only_ascii=True)}
                                        )[0]
                                    except Exception as e:
                                        logger.error(e)
                                        continue
                                elif k == "tag":
                                    try:
                                        tag, tag_created = Tag.objects.get_or_create(
                                            name=item[k]['name'],
                                            slug=item[k]['slug'],
                                        )
                                    except Exception as e:
                                        logger.error(e)
                                        continue
                                    else:
                                        # Delete our special key, InventoryItem does not have this key in its model
                                        # FIXME: Should we delete this?
                                        del item[k]
                                elif k == "name":
                                    # Shorten string
                                    item[k] = item[k][:64]
                                elif (k == "serial" or k == "part_id" or k == "asset_tag"):
                                    # Shorten string
                                    item[k] = item[k][:50]
                                elif k == "description":
                                    # Shorten string
                                    item[k] = item[k][:200]

                            item['discovered'] = True
                            logger.info(
                                f'Updating item {item} for the device {device.name}')

                            # Continue the loop if we couldn't add an item. Report an error and add Journal entry
                            try:
                                inventory_item, item_created = InventoryItem.objects.get_or_create(
                                    device=device, asset_tag=item['asset_tag'], defaults={**item})
                            except Exception as e:
                                logger.error(e)
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_WARNING,
                                        comments=f'Item {item} was not updated for the device {device.name} due to the error {e}'
                                    ),
                                )
                                continue

                            if (not item_created):
                                logger.info(
                                    f'Updating item with the asset_tag {inventory_item.asset_tag} for the device {device.name}')
                                inventory_item.snapshot()
                                # FIXME: Will it work with tags if they differ or if there are more than one?
                                # FIXME: Actually, we do not check for tags here, the 'tag' key has been deleted already! See below the tags.add()
                                for k, v in item.items():
                                    if (getattr(inventory_item, k) != item[k]):
                                        setattr(inventory_item, k, v)
                                        item_updated = True
                                # Add tag. Do not skip if we could not add the tag, but report the error and add a Journal entry.
                                if (tag is not None):
                                    if (not tag in inventory_item.tags.all()):
                                        try:
                                            # FIXME: What if this tag already exists? Will it be duplicated?
                                            inventory_item.tags.add(tag)
                                        except Exception as e:
                                            logger.error(e)
                                            journal_entries.append(
                                                JournalEntry(
                                                    assigned_object=device,
                                                    created_by=user,
                                                    kind=JournalEntryKindChoices.KIND_WARNING,
                                                    comments=f'Tag {tag} was not updated for the inventory item {inventory_item.name} due to the error {e}'
                                                ),
                                            )
                                        else:
                                            item_updated = True

                                if (item_updated):
                                    inventory_item.save()
                                    log = inventory_item.to_objectchange(
                                        action_update)
                                    log.user = user
                                    log.request_id = _uuid
                                    log.save()
                                    journal_entries.append(
                                        JournalEntry(
                                            assigned_object=device,
                                            created_by=user,
                                            kind=JournalEntryKindChoices.KIND_INFO,
                                            comments=f'Updated item with the asset_tag {inventory_item.asset_tag} for the device {device.name}'
                                        ),
                                    )

                                    journal_entries.append(
                                        JournalEntry(
                                            assigned_object=inventory_item,
                                            created_by=user,
                                            kind=JournalEntryKindChoices.KIND_INFO,
                                            comments=f'Updated item with the asset_tag {inventory_item.asset_tag} for the device {device.name}'
                                        ),
                                    )
                            else:
                                logger.info(
                                    f'Creating new item with the asset_tag {inventory_item.asset_tag} for the device {device.name}')
                                # Add tag. Do not skip if we could not add the tag, but report the error and add a Journal entry.
                                if (tag is not None):
                                    try:
                                        inventory_item.tags.add(tag)
                                    except Exception as e:
                                        logger.error(e)
                                        journal_entries.append(
                                            JournalEntry(
                                                assigned_object=device,
                                                created_by=user,
                                                kind=JournalEntryKindChoices.KIND_WARNING,
                                                comments=f'Tag {tag} was not updated for the inventory item {inventory_item.name} due to the error {e}'
                                            ),
                                        )

                                # Report about just created inventory item
                                inventory_item.save()
                                log = inventory_item.to_objectchange(
                                    action_create)
                                log.user = user
                                log.request_id = _uuid
                                log.save()
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=device,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_INFO,
                                        comments=f'Added a new inventory item {inventory_item.name} to the device {device.name}'
                                    ),
                                )
                                journal_entries.append(
                                    JournalEntry(
                                        assigned_object=inventory_item,
                                        created_by=user,
                                        kind=JournalEntryKindChoices.KIND_INFO,
                                        comments=f'Added a new inventory item {inventory_item.name} to the device {device.name}'
                                    ),
                                )

            # Post journal entries in a bulk
            JournalEntry.objects.bulk_create(journal_entries)

    else:
        # TODO: We must report such devices via email
        logger.error(
            f'Device {device_dict} does not contain a serial. Skipping.')


def soup_to_dict(soup):
    config = PLUGIN_SETTINGS
    device = {}
    items = {}
    for k, v in config.items():
        if v:
            value_type, content = v.split(':', 1)
            if value_type == "xml":
                path, tag = content.rsplit('.', 1)
                device[k] = xmlpath_or_unknown(soup, path, tag)
            elif value_type == "object":
                obj_type, value = content.split(':', 1)
                if value.isdigit():
                    device[k] = eval(
                        obj_type + ".objects.filter(id=" + value + ")[0]")
                else:
                    device[k] = eval(obj_type + ".objects.get_or_create(name='" +
                                     value + "', slug=slugify('" + value + "', only_ascii=True))")[0]
            elif value_type == "lazy":
                # Leave lazy for the second loop
                # FIXME: Too simple, we should support nested variables.
                # FIXME: Requires two loops, not optimal
                device[k] = v
        else:
            device[k] = v

    # Second loop for "lazy:" variables and serial->upper()
    # FIXME: Not optimal and dirty
    for k, v in device.items():
        # FIXME: Dirty upcase for device serial. We can't do other way right now.
        if (k == 'serial' and v and isinstance(v, str)):
            device[k] = v.upper()
        if (v and isinstance(v, str) and ':' in v):
            value_type, content = v.split(':', 1)
            if value_type == "lazy":
                # FIXME: Not all fields must be <= 50 length
                try:
                    device[k] = eval(content)
                except Exception as e:
                    logger.error(e)
                    continue

    for k, v in inventory_settings.items():
        items[k] = []
        for xml in soup.find_all(k):
            item = {}
            for k1, v1 in v.items():
                if (v1):
                    if not (isinstance(v1, str) and v1.startswith('lazy:')):
                        # print(f"First loop parse key is: {k1}, value is {v1}")
                        try:
                            item[k1] = eval(v1)
                        except Exception as e:
                            item[k1] = "ERROR"
                            logger.error(e)
                            continue
                    else:
                        item[k1] = v1
            # Second loop for "lazy:" variables and deleting None vars, iterate over already parsed "item" items
            # FIXME: Not optimal and dirty
            for k1, v1 in list(item.items()):
                if (v1):
                    if (isinstance(v1, str) and v1.startswith('lazy:')):
                        # print(f"Second loop parse key is: {k1}, value is {v1}")
                        value_type, content = v1.split(':', 1)
                        item[k1] = eval(content)
                elif (v1 is None):
                    # print(f"Deleting key {k1} because its value is None")
                    del item[k1]

            items[k].append(item)
    return device, items
