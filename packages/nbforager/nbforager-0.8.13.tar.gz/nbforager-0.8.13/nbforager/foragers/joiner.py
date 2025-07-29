"""Joiner."""

from operator import itemgetter

from vhelpers import vlist

from nbforager import helpers as h
from nbforager.api.base_c import BaseC
from netports import IPv4
from nbforager.nb_tree import NbTree
from nbforager.parser import nb_parser
from nbforager.parser.nb_value import NbValue
from nbforager.types_ import LDAny, DAny, LStr, DiDAny, LInt, DiLDAny, SInt


class Joiner:
    """Helper methods are used to create additional keys in Netbox objects,

    representing them similarly to the WEB UI.
    """

    def __init__(self, tree: NbTree):
        """Init Joiner.
        :param NbTree tree: Contains Netbox that need to be updated similar to the WEB UI.
        """
        self.tree = tree

    # noinspection PyProtectedMember
    def init_extra_keys(self) -> None:
        """Init extra keys to represent Netbox objects similar to the WEB UI.

        :return: None. Update NbTree object.
        """
        for app, model in [
            ("dcim", "devices"),
            ("dcim", "interfaces"),
            ("virtualization", "virtual_machines"),
            ("virtualization", "interfaces"),
        ]:
            key = h.attr_to_model(f"{app}/{model}/")
            extra_keys: LStr = BaseC._extra_keys[key]  # pylint: disable=W0212
            objects_d: DiDAny = getattr(getattr(self.tree, app), model)
            for object_d in objects_d.values():
                for _key in extra_keys:
                    object_d[_key] = {}

        for model, key, strict in [
            ("aggregates", "prefix", True),
            ("prefixes", "prefix", True),
            ("ip_addresses", "address", False),
        ]:
            objects: DiDAny = getattr(self.tree.ipam, model)
            for data in objects.values():
                nbv = NbValue(data=data)
                family: int = nbv.family_value()
                if family != 4:
                    continue
                snet = data[key]
                data["_ipv4"] = IPv4(snet, strict=strict)
                data["_aggregate"] = {}  # DAny
                data["_super_prefix"] = {}  # DAny
                data["_sub_prefixes"] = []  # LDAny
                data["_ip_addresses"] = []  # LDAny

    def join_dcim_devices(self) -> None:
        """Create additional keys to represent dcim.devices similar to the WEB UI.

            In dcim.devices:

            - ``_console_ports``
            - ``_console_server_ports``
            - ``_device_bays``
            - ``_front_ports``
            - ``_interfaces``
            - ``_inventory_items``
            - ``_module_bays``
            - ``_power_outlets``
            - ``_power_ports``
            - ``_rear_ports``
            - ``_vc_members``

            In dcim.interfaces:

            - ``_ip_addresses``

        :return: None. Update NbTree object.
        """
        self._join_virtual_chassis()
        intf_ids: LInt = self._join_dcim_devices()
        self._join_ip_addresses(intf_ids, app="dcim")

    def _join_virtual_chassis(self):
        """Add virtual-chassis members to master devices.

        :return: None. Update data in object.
        """
        app = "dcim"
        model = "devices"
        nbf_devices: DiDAny = getattr(getattr(self.tree, app), model)

        for member_id, device_d in nbf_devices.items():
            if device_d["virtual_chassis"]:
                master_id: int = device_d["virtual_chassis"]["master"]["id"]
                if member_id != master_id:
                    if master_d := nbf_devices.get(master_id, {}):
                        master_d["_vc_members"][member_id] = nbf_devices[member_id]

    def _join_dcim_devices(self) -> LInt:
        """Create additional key/values to represent devices similar to the WEB UI.

        Create key/values: _interfaces, _front_ports, _console_ports, etc.

        :return: IDs of joined ports. Update NbTree.dcim.devices object.
        """
        # models
        app = "dcim"
        model = "devices"
        # noinspection PyProtectedMember
        extra_keys: LStr = BaseC._extra_keys["dcim/devices/"]  # pylint: disable=W0212
        extra_keys = [s for s in extra_keys if s != "_vc_members"]
        extra_models: LStr = [s.lstrip("_") for s in extra_keys]
        nbf_devices: DiDAny = getattr(getattr(self.tree, app), model)

        # joined interfaces, need find assigned ip-addresses
        intf_ids: SInt = set()

        # set  _interfaces, _front_ports, etc.
        for extra_model in extra_models:
            ports_d: DiDAny = getattr(getattr(self.tree, app), extra_model)
            for nb_port in ports_d.values():
                port_name = nb_port["name"]
                device_id: int = nb_port["device"]["id"]
                nb_device: DAny = nbf_devices.get(device_id, {})
                extra_key = f"_{extra_model}"

                # if device has been downloaded from netbox
                if extra_key in nb_device:
                    nb_device[extra_key][port_name] = nb_port

                    # interface ids to assign ip_addresses
                    if extra_model == "interfaces":
                        intf_id = nb_port["id"]
                        intf_ids.add(intf_id)

        # join virtual chassis interfaces to master
        for device_id, nb_device in nbf_devices.items():
            for vc_member in nb_device["_vc_members"].values():
                master_id = vc_member["virtual_chassis"]["master"]["id"]
                if device_id == master_id:
                    for intf_name, nb_intf in vc_member["_interfaces"].items():
                        if intf_name not in nb_device["_interfaces"]:
                            nb_device["_interfaces"][intf_name] = nb_intf

        return sorted(intf_ids)

    def _join_ip_addresses(self, intf_ids: LInt, app: str) -> None:
        """Add NbTree.ipam.ip_address data to NbTree.dcim.interfaces._ip_addresses or VM.

        :param intf_ids: Interface IDs that was joined in device/VM.
        :param app: Application name: "dcim", "virtualization"

        :return: None. Update NbTree.ipam.ip_addresses.
        """
        model = "interfaces"
        object_type = "virtualization.vminterface" if app == "virtualization" else "dcim.interface"
        intfs_d: DiDAny = getattr(getattr(self.tree, app), model)
        params = {"id": intf_ids}
        intfs_d = {
            d["id"]: d for d in nb_parser.find_objects(objects=list(intfs_d.values()), **params)
        }

        app = "ipam"
        extra_model = "ip_addresses"
        extra_key = f"_{extra_model}"
        nbf_addresses: DiDAny = getattr(getattr(self.tree, app), extra_model)

        for nb_addr in nbf_addresses.values():
            address = nb_addr["address"]
            if nb_addr["assigned_object_type"] == object_type:
                if assigned_object_id := nb_addr["assigned_object_id"]:
                    nb_intf: DAny = intfs_d.get(assigned_object_id, {})  # pylint: disable=E1101

                    # if device has been downloaded from netbox
                    if extra_key in nb_intf:
                        nb_intf[extra_key][address] = nb_addr

    def join_ipam_ipv4(self) -> None:
        """Create additional keys to represent ipam similar to the WEB UI.

            Add new attributes in ipam.aggregate, ipam.prefixes, ipam.ip_addresses:

            - ``_ipv4`` IPv4 object
            - ``_aggregate`` Aggregate data for ipam.prefixes and ipam.ip_addresses
            - ``_super_prefix`` Related parent prefix data for ipam.prefixes and ipam.ip_addresses
            - ``_sub_prefixes`` Related child prefixes data for ipam.prefixes and ipam.ip_addresses
            - ``_ip_addresses`` Related IP addresses data for ipam.aggregates and ipam.prefixes

        :return: None. Update NbTree object.
        """
        self._join_ipam_aggregates()
        self._join_ipam_prefixes()
        self._join_ipam_ip_addresses()
        self._join_update_sub_prefixes()

    def _join_ipam_aggregates(self) -> None:
        """Add prefixes to tree.ipam.aggregates._sub_prefixes."""
        aggregates: LDAny = self._get_aggregates_ip4()
        prefixes_d: DiLDAny = self._get_prefixes_ip4_d()
        for aggregate in aggregates:
            for depth, prefixes in prefixes_d.items():
                for prefix in prefixes:
                    _aggregate = aggregate["prefix"]
                    _prefix = prefix["prefix"]
                    if prefix["_ipv4"] in aggregate["_ipv4"]:
                        prefix["_aggregate"] = aggregate
                        if depth == 0:
                            aggregate["_sub_prefixes"].append(prefix)

    def _join_ipam_ip_addresses(self) -> None:
        """Add prefixes to tree.ipam.ip-addresses._super_prefix."""
        ip_addresses: LDAny = self._get_ip_addresses_ip4()
        prefixes_d: DiLDAny = self._get_prefixes_ip4_d()
        depths: LInt = list(prefixes_d)
        depths.reverse()

        added_addresses: LDAny = []
        for depth in depths:
            ip_addresses_ = ip_addresses.copy()
            prefixes: LDAny = prefixes_d.get(depth, [])
            for ip_address in ip_addresses_:
                for prefix in prefixes:
                    if ip_address["_ipv4"] not in prefix["_ipv4"]:
                        continue
                    if ip_address in added_addresses:
                        continue
                    ip_address["_aggregate"] = prefix["_aggregate"]
                    ip_address["_super_prefix"] = prefix
                    prefix["_ip_addresses"].append(ip_address)
                    added_addresses.append(ip_address)
            ip_addresses = [d for d in ip_addresses if d not in added_addresses]

    def _join_ipam_prefixes(self) -> None:
        """Add prefixes to tree.ipam.prefixes._sub_prefixes, _super_prefix"""
        super_prefixes = []
        prefixes_d: DiLDAny = self._get_prefixes_ip4_d()
        for depth, sub_prefixes in enumerate(prefixes_d.values()):
            if not depth:
                super_prefixes = sub_prefixes
                continue
            for super_prefix in super_prefixes:
                if super_prefix["_ipv4"].len == 32:
                    continue
                for sub_prefix in sub_prefixes:
                    if sub_prefix["_ipv4"] in (super_prefix["_ipv4"]):
                        super_prefix["_sub_prefixes"].append(sub_prefix)
                        sub_prefix["_super_prefix"] = super_prefix
            super_prefixes = sub_prefixes

    def _join_update_sub_prefixes(self) -> None:
        """Update _sub_prefixes in ipam.aggregates and ipam.prefixes.

        Remove duplicates, remove objects with improper depth, sort by IPv4.
        """
        aggregates = self._get_aggregates_ip4()
        for aggregate in aggregates:
            sub_prefixes = vlist.no_dupl(aggregate["_sub_prefixes"])
            sub_prefixes = [d for d in sub_prefixes if not d["_super_prefix"]]
            aggregate["_sub_prefixes"] = sorted(sub_prefixes, key=itemgetter("_ipv4"))

        prefixes = self._get_prefixes_ip4()
        for prefix in prefixes:
            sub_prefixes = vlist.no_dupl(prefix["_sub_prefixes"])
            prefix["_sub_prefixes"] = sorted(sub_prefixes, key=itemgetter("_ipv4"))
            ip_addresses = vlist.no_dupl(prefix["_ip_addresses"])
            prefix["_ip_addresses"] = sorted(ip_addresses, key=itemgetter("_ipv4"))

    # ============================= helpers ==============================

    def _get_aggregates_ip4(self) -> LDAny:
        """Return ipam.aggregates family=4 sorted by IPv4."""
        aggregates: LDAny = list(self.tree.ipam.aggregates.values())
        aggregates = [d for d in aggregates if d["family"]["value"] == 4]
        return sorted(aggregates, key=itemgetter("_ipv4"))

    def _get_ip_addresses_ip4(self) -> LDAny:
        """Return ipam.ip_addresses family=4 sorted by IPv4."""
        ip_addresses: LDAny = list(self.tree.ipam.ip_addresses.values())
        ip_addresses = [d for d in ip_addresses if d["family"]["value"] == 4 and d["vrf"] is None]
        return sorted(ip_addresses, key=itemgetter("_ipv4"))

    def _get_prefixes_ip4(self) -> LDAny:
        """Return ipam.prefixes family=4 sorted by IPv4."""
        prefixes: LDAny = list(self.tree.ipam.prefixes.values())
        prefixes = [d for d in prefixes if d["family"]["value"] == 4 and d["vrf"] is None]
        return sorted(prefixes, key=itemgetter("_ipv4"))

    def _get_prefixes_ip4_d(self) -> DiLDAny:
        """Split prefixes by depth.

        :return: A dictionary of prefixes where the key represents the depth
            and the value represents a list of prefixes at that depth.
        """
        prefixes: LDAny = self._get_prefixes_ip4()
        prefixes_d: DiLDAny = {d["_depth"]: [] for d in prefixes}
        for prefix in prefixes:
            depth = int(prefix["_depth"])
            prefixes_d[depth].append(prefix)
        return prefixes_d
