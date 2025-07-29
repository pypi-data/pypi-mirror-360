from netbox.plugins import PluginConfig


class FusionInventoryConfig(PluginConfig):
    """
    This class defines attributes for the NetBox FI Gateway plugin.
    """
    # Plugin package name
    name = 'netbox_fusioninventory_plugin'
    # Human-friendly name and description
    verbose_name = 'Fusion inventory plugin'
    description = 'A Plugin for import devices and their components from fusion inventory agent'

    # Plugin version
    version = '0.7'

    # Plugin author
    author = 'Michaël Ricart'
    author_email = 'michael.ricart@0w.tf'

    # Configuration parameters that MUST be defined by the user (if any)
    required_settings = []

    # Default configuration parameter values, if not set by the user
    default_settings = {
        "name":"xml:request.content.hardware.name",
        "role":"object:DeviceRole:unknown",
        "tenant":None,
        "manufacturer":"xml:request.content.bios.mmanufacturer",
        "device_type":"xml:request.content.bios.mmodel",
        "platform":"xml:request.content.hardware.osname",
        "serial":"xml:request.content.hardware.uuid",
        "asset_tag":"lazy:'WKS-'+device['serial']",
        "status":"str:active",
        "site":"object:Site:unknown",
        "location":None,
        "rack":None,
        "position":None,
        "face":None,
        "virtual_chassis":None,
        "vc_position":None,
        "vc_priority":None,
        "cluster":None,
        "comments":None,
    }

    

    # Base URL path. If not set, the plugin name will be used.
    base_url = 'fusion-inventory'

    # Caching config
    caching_config = {}


config = FusionInventoryConfig

