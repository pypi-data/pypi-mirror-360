# pylint: disable=too-many-public-methods

"""NbValue."""

import re

from nbforager.exceptions import NbParserError
from nbforager.parser.nb_parser import NbParser, check_strict
from nbforager.types_ import LStr, LInt, LDAny

RE_PREFIX = r"\d+\.\d+\.\d+\.\d+/\d+"  # Regular expression for matching IP address prefix


class NbValue(NbParser):
    """Dictionary parser for extracting values from a Netbox object using a chain of keys.

    Netbox object may have None instead of a dictionary when a related object is absent,
    requiring constant data type checks. NbParser ensures the desired value is returned
    with the correct data type, even if the data is missing.

    Raises NbParserError if strict=True and some keys are missing.
    """

    @check_strict
    def a_terminations(self) -> list:
        """dcim/cables/a_terminations."""
        return self.list("a_terminations")

    @check_strict
    def a_terminations_object_circuit_cid(self) -> LStr:
        """dcim/cables/a_terminations/0/object/circuit/cid."""
        items: LDAny = self.list("a_terminations")
        values: LStr = [str(d["object"]["circuit"]["cid"]) for d in items]
        return values

    @check_strict
    def a_terminations_object_circuit_id(self) -> LInt:
        """dcim/cables/a_terminations/0/object/circuit/id."""
        items: LDAny = self.list("a_terminations")
        values: LInt = [int(d["object"]["circuit"]["id"]) for d in items]
        return values

    @check_strict
    def a_terminations_object_cable(self) -> LInt:
        """dcim/cables/a_terminations/0/object/cable."""
        items: LDAny = self.list("a_terminations")
        values: LInt = [int(d["object"]["cable"]) for d in items]
        return values

    @check_strict
    def a_terminations_object_id(self) -> LInt:
        """dcim/cables/a_terminations/0/object/id."""
        items: LDAny = self.list("a_terminations")
        values: LInt = [int(d["object"]["id"]) for d in items]
        return values

    @check_strict
    def a_terminations_object_term_side(self) -> LStr:
        """dcim/cables/a_terminations/0/object/term_side."""
        items: LDAny = self.list("a_terminations")
        values: LStr = [str(d["object"]["term_side"]) for d in items]
        return values

    @check_strict
    def a_terminations_object_type(self) -> LStr:
        """dcim/cables/a_terminations/0/object_type."""
        items: LDAny = self.list("a_terminations")
        values: LStr = [str(d["object_type"]) for d in items]
        return values

    def address(self) -> str:
        """ipam/ip-addresses/address."""
        address = self.str("address")
        if self.strict and not self._is_prefix(subnet=address):
            raise NbParserError(f"address A.B.C.D/LEN expected in {self.data}.")
        return address

    @check_strict
    def assigned_device_name(self) -> str:
        """ipam/ip-addresses/assigned_object/device/name."""
        return self.str("assigned_object", "device", "name")

    @check_strict
    def b_terminations(self) -> list:
        """dcim/cables/b_terminations."""
        return self.list("b_terminations")

    @check_strict
    def b_terminations_object_circuit_cid(self) -> LStr:
        """dcim/cables/b_terminations/0/object/circuit/cid."""
        items: LDAny = self.list("b_terminations")
        values: LStr = [str(d["object"]["circuit"]["cid"]) for d in items]
        return values

    @check_strict
    def b_terminations_object_circuit_id(self) -> LInt:
        """dcim/cables/b_terminations/0/object/circuit/id."""
        items: LDAny = self.list("b_terminations")
        values: LInt = [int(d["object"]["circuit"]["id"]) for d in items]
        return values

    @check_strict
    def b_terminations_object_cable(self) -> LInt:
        """dcim/cables/b_terminations/0/object/cable."""
        items: LDAny = self.list("b_terminations")
        values: LInt = [int(d["object"]["cable"]) for d in items]
        return values

    @check_strict
    def b_terminations_object_id(self) -> LInt:
        """dcim/cables/b_terminations/0/object/id."""
        items: LDAny = self.list("b_terminations")
        values: LInt = [int(d["object"]["id"]) for d in items]
        return values

    @check_strict
    def b_terminations_object_term_side(self) -> LStr:
        """dcim/cables/b_terminations/0/object/term_side."""
        items: LDAny = self.list("b_terminations")
        values: LStr = [str(d["object"]["term_side"]) for d in items]
        return values

    @check_strict
    def b_terminations_object_type(self) -> LStr:
        """dcim/cables/b_terminations/0/object_type."""
        items: LDAny = self.list("b_terminations")
        values: LStr = [str(d["object_type"]) for d in items]
        return values

    @check_strict
    def cable_id(self) -> int:
        """circuits/circuit-terminations/cable/id."""
        return self.int("cable", "id")

    @check_strict
    def cable_display(self) -> str:
        """circuits/circuit-terminations/cable/display."""
        return self.str("cable", "display")

    @check_strict
    def cable_end(self) -> str:
        """circuits/circuit-terminations/cable_end."""
        return self.str("cable_end")

    @check_strict
    def cable_label(self) -> str:
        """circuits/circuit-terminations/cable/label."""
        return self.str("cable", "label")

    @check_strict
    def cid(self) -> str:
        """ipam/circuits/circuits/cid."""
        return self.str("cid")

    @check_strict
    def circuit_count(self) -> int:
        """ipam/circuits/circuit-types/circuit_count."""
        return self.int("circuit_count")

    @check_strict
    def circuit_id(self) -> int:
        """circuits/circuit-terminations/circuit/id."""
        return self.int("circuit", "id")

    @check_strict
    def circuit_cid(self) -> str:
        """circuits/circuit-terminations/circuit/cid."""
        return self.str("circuit", "cid")

    @check_strict
    def cluster_id(self) -> int:
        """virtualization/virtual-machines/cluster/id."""
        return self.int("cluster", "id")

    @check_strict
    def cluster_name(self) -> str:
        """virtualization/virtual-machines/cluster/name."""
        return self.str("cluster", "name")

    @check_strict
    def color(self) -> str:
        """circuits/circuit-types/color."""
        return self.str("color")

    @check_strict
    def comments(self) -> str:
        """dcim/devices/comments."""
        return self.str("comments")

    @check_strict
    def connected_endpoints(self) -> list:
        """dcim/interfaces/connected_endpoints."""
        return self.list("connected_endpoints")

    @check_strict
    def connected_endpoints_id(self) -> LInt:
        """dcim/interfaces/connected_endpoints/0/id."""
        connected_endpoints = self.list("connected_endpoints")
        ids: LInt = [int(d["id"]) for d in connected_endpoints]
        return ids

    @check_strict
    def connected_endpoints_name(self) -> LStr:
        """dcim/interfaces/connected_endpoints/0/name."""
        connected_endpoints = self.list("connected_endpoints")
        names: LStr = [str(d["name"]) for d in connected_endpoints]
        return names

    @check_strict
    def connected_endpoints_type(self) -> str:
        """dcim/interfaces/connected_endpoints_type."""
        return self.str("connected_endpoints_type")

    @check_strict
    def connected_endpoints_reachable(self) -> bool:
        """dcim/interfaces/connected_endpoints_reachable."""
        return bool(self.data.get("connected_endpoints_reachable"))

    @check_strict
    def created(self) -> str:
        """dcim/devices/created."""
        return self.str("created")

    @check_strict
    def custom_fields(self) -> dict:
        """circuits/circuit-terminations/custom_fields."""
        return self.dict("custom_fields")

    @check_strict
    def description(self) -> str:
        """dcim/devices/description."""
        return self.str("description")

    @check_strict
    def device_id(self) -> int:
        """dcim/console-ports/device/id."""
        return self.int("device", "id")

    @check_strict
    def device_name(self) -> str:
        """dcim/console-ports/device/name."""
        return self.str("device", "name")

    @check_strict
    def device_type_id(self) -> int:
        """dcim/devices/device_type/id."""
        return self.int("device_type", "id")

    @check_strict
    def device_type_manufacturer_id(self) -> int:
        """dcim/devices/device_type/manufacturer/id."""
        return self.int("device_type", "manufacturer", "id")

    @check_strict
    def device_type_manufacturer_name(self) -> str:
        """dcim/devices/device_type/manufacturer/name."""
        return self.str("device_type", "manufacturer", "name")

    @check_strict
    def device_type_manufacturer_slug(self) -> str:
        """dcim/devices/device_type/manufacturer/slug."""
        return self.str("device_type", "manufacturer", "slug")

    @check_strict
    def device_type_model(self) -> str:
        """dcim/devices/device_type/model."""
        return self.str("device_type", "model")

    @check_strict
    def device_type_slug(self) -> str:
        """dcim/devices/device_type/slug."""
        return self.str("device_type", "slug")

    @check_strict
    def device_role_id(self) -> int:
        """dcim/devices/device_role/id."""
        return self.int("device_role", "id")

    @check_strict
    def device_role_name(self) -> str:
        """dcim/devices/device_role/name."""
        return self.str("device_role", "name")

    @check_strict
    def device_role_slug(self) -> str:
        """dcim/devices/device_role/slug."""
        return self.str("device_role", "slug")

    @check_strict
    def display(self) -> str:
        """ipam/aggregates/display."""
        return self.str("display")

    @check_strict
    def dns_name(self) -> str:
        """ipam/ip-addresses/dns_name."""
        return self.str("dns_name")

    def enabled(self) -> bool:
        """dcim/interfaces/enabled."""
        return bool(self.data.get("enabled"))

    @check_strict
    def export_targets(self) -> list:
        """ipam/vrfs/export_targets."""
        return self.list("export_targets")

    @check_strict
    def export_targets_id(self) -> LInt:
        """ipam/vrfs/export_targets/0/id."""
        export_targets = self.list("export_targets")
        ids: LInt = [int(d["id"]) for d in export_targets]
        return ids

    @check_strict
    def export_targets_name(self) -> LStr:
        """ipam/vrfs/export_targets/0/name."""
        export_targets = self.list("export_targets")
        names: LStr = [str(d["name"]) for d in export_targets]
        return names

    @check_strict
    def face_value(self) -> str:
        """dcim/devices/face/value."""
        return self.str("face", "value")

    @check_strict
    def family_value(self) -> int:
        """ipam/prefixes/family/value."""
        return self.int("family", "value")

    @check_strict
    def group_name(self) -> str:
        """imap/vlans/group/name."""
        return self.str("group", "name")

    def id_(self) -> int:
        """ipam/prefixes/id."""
        return self.int("id")

    @check_strict
    def import_targets(self) -> list:
        """ipam/vrfs/import_targets."""
        return self.list("import_targets")

    @check_strict
    def import_targets_id(self) -> LInt:
        """ipam/vrfs/import_targets/0/id."""
        import_targets = self.list("import_targets")
        ids: LInt = [int(d["id"]) for d in import_targets]
        return ids

    @check_strict
    def import_targets_name(self) -> LStr:
        """ipam/vrfs/import_targets/0/name."""
        import_targets = self.list("import_targets")
        names: LStr = [str(d["name"]) for d in import_targets]
        return names

    def is_pool(self) -> bool:
        """ipam/prefixes/is_pool."""
        return bool(self.data.get("is_pool"))

    def is_private(self) -> bool:
        """ipam/rirs/is_private."""
        return bool(self.data.get("is_private"))

    @check_strict
    def label(self) -> str:
        """dcim/cables/label."""
        return self.str("label")

    @check_strict
    def last_updated(self) -> str:
        """dcim/devices/last_updated."""
        return self.str("last_updated")

    @check_strict
    def link_peers(self) -> list:
        """circuits/circuit-terminations/link_peers."""
        return self.list("link_peers")

    @check_strict
    def link_peers_cable(self) -> LStr:
        """circuits/circuit-terminations/link_peers/0/cable."""
        link_peers = self.list("link_peers")
        cables: LStr = [str(d["cable"]) for d in link_peers]
        return cables

    @check_strict
    def link_peers_id(self) -> LInt:
        """circuits/circuit-terminations/link_peers/0/id."""
        link_peers = self.list("link_peers")
        ids: LInt = [int(d["id"]) for d in link_peers]
        return ids

    @check_strict
    def link_peers_name(self) -> LStr:
        """circuits/circuit-terminations/link_peers/0/name."""
        link_peers = self.list("link_peers")
        names: LStr = [str(d["name"]) for d in link_peers]
        return names

    @check_strict
    def link_peers_type(self) -> str:
        """circuits/circuit-terminations/link_peers_type."""
        return self.str("link_peers_type")

    @check_strict
    def manufacturer_id(self) -> int:
        """dcim/device-types/manufacturer/id."""
        return self.int("manufacturer", "id")

    @check_strict
    def manufacturer_name(self) -> str:
        """dcim/device-types/manufacturer/name."""
        return self.str("manufacturer", "name")

    @check_strict
    def manufacturer_slug(self) -> str:
        """dcim/device-types/manufacturer/name."""
        return self.str("manufacturer", "slug")

    def occupied(self) -> bool:
        """dcim/devices/_occupied."""
        return bool(self.data.get("_occupied"))

    @check_strict
    def model(self) -> str:
        """dcim/device-types/model."""
        return self.str("model")

    @check_strict
    def name(self) -> str:
        """dcim/devices/name, dcim/vlans/name."""
        return self.str("name")

    def mark_connected(self) -> bool:
        """dcim/interfaces/mark_connected."""
        return bool(self.data.get("mark_connected"))

    def mark_utilized(self) -> bool:
        """ipam/prefixes/mark_utilized."""
        return bool(self.data.get("mark_utilized"))

    @check_strict
    def part_number(self) -> str:
        """dcim/device-types/part_number."""
        return self.str("part_number")

    @check_strict
    def platform_id(self) -> int:
        """dcim/devices/platform/id."""
        return self.int("platform", "id")

    @check_strict
    def platform_name(self) -> str:
        """dcim/devices/platform/name."""
        return self.str("platform", "name")

    @check_strict
    def platform_slug(self) -> str:
        """dcim/devices/platform/slug."""
        return self.str("platform", "slug")

    def prefix(self) -> str:
        """ipam/prefixes/prefix, ipam/aggregates/prefix.

        :return: Prefix with length A.B.C.D/LEN.

        :raise NbParserError: if strict=True and the prefix does not match the naming
            convention A.B.C.D/LEN.
        """
        prefix = self.str("prefix")
        if self.strict and not self._is_prefix(subnet=prefix):
            raise NbParserError(f"prefix expected in {self.data}.")
        return prefix

    def primary_ip4(self) -> str:
        """dcim/devices/primary_ip4/address.

        :return: primary_ip4 address.

        :raise NbParserError: if strict=True and device has no primary_ip4 address.
        """
        try:
            primary_ip4 = self.data["primary_ip4"]["address"]
        except (KeyError, TypeError):
            primary_ip4 = ""
        if not isinstance(primary_ip4, str):
            primary_ip4 = ""

        if self.strict:
            if not primary_ip4:
                raise NbParserError(f"primary_ip4/address expected in {self.data}.")
            if not re.match(r"^\d+\.\d+\.\d+\.\d+(/\d+)?$", primary_ip4):
                raise NbParserError(f"primary_ip4/address A.B.C.D expected in {self.data}.")
        return primary_ip4

    def primary_ip(self) -> str:
        """dcim/devices/primary_ip4/address.

        :return: primary ip address without mask.

        :raise NbParserError: if strict=True and device has no primary_ip4 address.
        """
        ip4 = self.primary_ip4()
        ip = ip4.split("/", maxsplit=1)[0]
        return ip

    @check_strict
    def provider_id(self) -> int:
        """circuits/circuits/provider/id."""
        return self.int("provider", "id")

    @check_strict
    def provider_name(self) -> str:
        """circuits/circuits/provider/name."""
        return self.str("provider", "name")

    @check_strict
    def provider_slug(self) -> str:
        """circuits/circuits/provider/slug."""
        return self.str("provider", "slug")

    @check_strict
    def rack_id(self) -> int:
        """dcim/devices/rack/id."""
        return self.int("rack", "id")

    @check_strict
    def rack_name(self) -> str:
        """dcim/devices/rack/name."""
        return self.str("rack", "name")

    @check_strict
    def rd(self) -> str:
        """ipam/vrfs/rd."""
        return self.str("rd")

    @check_strict
    def rir_id(self) -> int:
        """ipam/aggregates/rir/id."""
        return self.int("rir", "id")

    @check_strict
    def rir_name(self) -> str:
        """ipam/aggregates/rir/name."""
        return self.str("rir", "name")

    @check_strict
    def rir_slug(self) -> str:
        """ipam/aggregates/rir/slug."""
        return self.str("rir", "slug")

    @check_strict
    def role_id(self) -> int:
        """dcim/devices/role/id."""
        return self.int("role", "id")

    @check_strict
    def role_name(self) -> str:
        """dcim/devices/role/name."""
        return self.str("role", "name")

    @check_strict
    def role_slug(self) -> str:
        """dcim/devices/role/slug."""
        return self.str("role", "slug")

    @check_strict
    def scope_id(self) -> int:
        """ipam/vlan-groups/scope/id."""
        return self.int("scope", "id")

    @check_strict
    def scope_name(self) -> str:
        """ipam/vlan-groups/scope/name."""
        return self.str("scope", "name")

    @check_strict
    def scope_slug(self) -> str:
        """ipam/vlan-groups/scope/slug."""
        return self.str("scope", "slug")

    @check_strict
    def scope_type(self) -> str:
        """ipam/vlan-groups/scope_type."""
        return self.str("scope_type")

    @check_strict
    def serial(self) -> str:
        """dcim/devices/serial."""
        return self.str("serial")

    @check_strict
    def site_id(self) -> int:
        """ipam/prefixes/site/id, dcim/devices/sites/id."""
        return self.int("site", "id")

    @check_strict
    def site_name(self, upper: bool = True) -> str:
        """ipam/prefixes/site/name, dcim/devices/sites/name.

        Convert site name to the same manner.
        Different objects have different upper or lower case:
        sites/name="SITE1",
        devices/site/name="SITE1",
        vlans/site/name="site1".

        :param upper: Whether to return the name in uppercase. Default is True.

        :return: Site name.

        :raise NbParserError: if strict=True and object has no site name.
        """
        site = self.str("site", "name").lower()
        if upper:
            site = site.upper()
        return site

    @check_strict
    def site_slug(self) -> str:
        """ipam/prefixes/site/slug, dcim/devices/sites/slug."""
        return self.str("site", "slug")

    @check_strict
    def slug(self) -> str:
        """ipam/roles/slug."""
        return self.str("slug")

    @check_strict
    def status_value(self) -> str:
        """ipam/prefixes/status/value."""
        return self.str("status", "value")

    def tags(self) -> LStr:
        """Get tag slugs from the data.

        :return: Slugs of tag.
        :rtype: List[str]
        """
        tags_ = self.list("tags")
        if not tags_:
            return []

        tags: LStr = []
        for tag_d in tags_:
            if tag := self._get_keys(type_=str, keys=["slug"], data=tag_d):
                tags.append(tag)
        return tags

    @check_strict
    def tenant_id(self) -> int:
        """ipam/aggregates/tenant/id."""
        return self.int("tenant", "id")

    @check_strict
    def tenant_name(self) -> str:
        """ipam/aggregates/tenant/name."""
        return self.str("tenant", "name")

    @check_strict
    def tenant_slug(self) -> str:
        """ipam/aggregates/tenant/name."""
        return self.str("tenant", "slug")

    @check_strict
    def term_side(self) -> str:
        """circuits/circuit-terminations/term_side."""
        return self.str("term_side")

    @check_strict
    def termination_a(self) -> dict:
        """ipam/circuits/circuits/termination_a."""
        return self.dict("termination_a")

    @check_strict
    def termination_a_id(self) -> int:
        """ipam/circuits/circuits/termination_a/id."""
        return self.int("termination_a", "id")

    @check_strict
    def termination_a_site_id(self) -> int:
        """ipam/circuits/circuits/termination_a/site/id."""
        return self.int("termination_a", "site", "id")

    @check_strict
    def termination_a_site_name(self) -> str:
        """ipam/circuits/circuits/termination_a/site/name."""
        return self.str("termination_a", "site", "name")

    @check_strict
    def termination_a_site_slug(self) -> str:
        """ipam/circuits/circuits/termination_a/site/slug."""
        return self.str("termination_a", "site", "slug")

    @check_strict
    def termination_a_provider_id(self) -> int:
        """ipam/circuits/circuits/termination_a/provider/id."""
        return self.int("termination_a", "provider", "id")

    @check_strict
    def termination_a_provider_name(self) -> str:
        """ipam/circuits/circuits/termination_a/provider/name."""
        return self.str("termination_a", "provider", "name")

    @check_strict
    def termination_a_xconnect_id(self) -> str:
        """ipam/circuits/circuits/termination_a/xconnect_id."""
        return self.str("termination_a", "xconnect_id")

    @check_strict
    def termination_z(self) -> dict:
        """ipam/circuits/circuits/termination_z."""
        return self.dict("termination_z")

    @check_strict
    def termination_z_id(self) -> int:
        """ipam/circuits/circuits/termination_z/id."""
        return self.int("termination_z", "id")

    @check_strict
    def termination_z_site_id(self) -> int:
        """ipam/circuits/circuits/termination_z/site/id."""
        return self.int("termination_z", "site", "id")

    @check_strict
    def termination_z_site_name(self) -> str:
        """ipam/circuits/circuits/termination_z/site/name."""
        return self.str("termination_z", "site", "name")

    @check_strict
    def termination_z_site_slug(self) -> str:
        """ipam/circuits/circuits/termination_z/site/slug."""
        return self.str("termination_z", "site", "slug")

    @check_strict
    def termination_z_provider_id(self) -> int:
        """ipam/circuits/circuits/termination_z/provider/id."""
        return self.int("termination_z", "provider", "id")

    @check_strict
    def termination_z_provider_name(self) -> str:
        """ipam/circuits/circuits/termination_z/provider/name."""
        return self.str("termination_z", "provider", "name")

    @check_strict
    def termination_z_xconnect_id(self) -> str:
        """ipam/circuits/circuits/termination_z/xconnect_id."""
        return self.str("termination_z", "xconnect_id")

    @check_strict
    def type_(self) -> str:
        """dcim/cables/type."""
        return self.str("type")

    @check_strict
    def type_id(self) -> int:
        """circuits/circuits/type/id."""
        return self.int("type", "id")

    @check_strict
    def type_name(self) -> str:
        """circuits/circuits/type/name."""
        return self.str("type", "name")

    @check_strict
    def type_slug(self) -> str:
        """circuits/circuits/type/slug."""
        return self.str("type", "slug")

    @check_strict
    def type_value(self) -> str:
        """dcim/console-ports/type/value."""
        return self.str("type", "value")

    def vid(self) -> int:
        """ipam/vlans/vid."""
        return self.int("vid")

    @check_strict
    def vlan_name(self) -> str:
        """ipam/prefixes/vlan/name."""
        return self.str("vlan", "name")

    def vlan_vid(self) -> int:
        """ipam/prefixes/vlan/vid."""
        return self.int("vlan", "vid")

    @check_strict
    def vrf_id(self) -> int:
        """ipam/ip-addresses/vrf/id."""
        return self.int("vrf", "id")

    @check_strict
    def vrf_name(self) -> str:
        """ipam/ip-addresses/vrf/name."""
        return self.str("vrf", "name")

    @check_strict
    def vrf_rd(self) -> str:
        """ipam/ip-addresses/vrf/rd."""
        return self.str("vrf", "rd")

    @check_strict
    def url(self) -> str:
        """ipam/prefixes/url."""
        return self.str("url")

    # ================================ is ================================

    def is_dcim(self, dcim: str) -> bool:
        """Check if object is dcim/devices.

        :return: True - if object is dcim/devices, False - otherwise.
        :rtype: bool

        :raise NbParserError: - if url is not /api/dcim/ and self.strict=True
        """
        try:
            url = self.data["url"]
            if re.search(f"/api/dcim/{dcim}/", url):
                return True
            return False
        except (KeyError, TypeError) as ex:
            if self.strict:
                raise NbParserError(f"invalid url in {self.data}.") from ex
            return False

    def is_ipam(self, ipam: str) -> bool:
        """Check If ipam url ipam is aggregate, prefix or address.

        :return: True - if aggregate, prefix, address, False - otherwise.
        :rtype: bool

        :raise NbParserError: If url is not aggregate or prefix or address
            and self.strict=True
        """
        try:
            url = self.data["url"]
            if re.search(f"/api/ipam/{ipam}/", url):
                return True
            return False
        except (KeyError, TypeError) as ex:
            if self.strict:
                raise NbParserError(f"ipam url expected in {self.data}.") from ex
            return False

    def is_vrf(self) -> bool:
        """Return True if data has vrf."""
        if self.data.get("vrf"):
            return True
        return False

    # ============================= helpers ==============================

    @staticmethod
    def _is_prefix(subnet: str) -> bool:
        """Return True if subnet has A.B.C.D/LEN format."""
        if re.match(rf"^{RE_PREFIX}$", subnet):
            return True
        return False
