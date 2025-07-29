"""NbCustom."""

import re
import string

from vhelpers import vlist, vre

from nbforager.parser.nb_value import NbValue, RE_PREFIX
from nbforager.types_ import SStr, T2Str, LStr, LInt


class NbCustom(NbValue):
    """Custom field parser.

    Dictionary parser for extracting values from a Netbox object using a chain of keys.

    Netbox object may have None instead of a dictionary when a related object is absent,
    requiring constant data type checks. NbParser ensures the desired value is returned
    with the correct data type, even if the data is missing.

    Raises NbParserError if strict=True and some keys are missing.
    """

    # ========================== custom_fields ===========================

    def cf_cloud_account(self) -> str:
        """ipam/aggregates/custom_fields/cloud_account/label."""
        return self.str("custom_fields", "cloud_account")

    def cf_end_of_support(self) -> str:
        """dcim/devices/custom_fields/end_of_support/value."""
        cf_value = self.str("custom_fields", "end_of_support").strip()
        return cf_value

    def cf_env(self) -> str:
        """ipam/prefixes/custom_fields/env/label."""
        return self.str("custom_fields", "env")

    def cf_recommended_vlans(self) -> LInt:
        """ipam/roles/custom_fields/recommended_vlans."""
        value = self.str("custom_fields", "recommended_vlans")
        vids: LInt = [int(s) for s in value.split(",") if s]
        vids = [i for i in vids if i]
        vids = vlist.no_dupl(vids)
        return vids

    def cf_required_env(self) -> bool:
        """ipam/roles/custom_fields/required_env."""
        return self.bool("custom_fields", "required_env")

    def cf_super_aggr(self) -> T2Str:
        """ipam/aggregates/custom_fields/super_aggregate/value."""
        value = self.str("custom_fields", "super_aggregate")
        value = value.strip()
        prefix, descr = vre.find2(f"^({RE_PREFIX})(.*)", value)
        return prefix, descr.strip()

    def cf_sw_planned(self) -> str:
        """dcim/devices/device-types/custom_fields/sw_planned."""
        return self.str("custom_fields", "sw_planned")

    def cf_sw_version(self) -> str:
        """dcim/devices/custom_fields/sw_version."""
        return self.str("custom_fields", "sw_version")

    # ========================= specific values ==========================

    def name(self) -> str:
        """dcim/devices/name, dcim/vlans/name.

        :return: Name value.

        :raise NbParserError: if object has no name.
        """
        strict_actual = self.strict
        self.strict = True
        name = super().name()
        self.strict = strict_actual
        return name

    def overlapped(self) -> str:
        """ipam/prefixes/overlapped."""
        return self.str("overlapped")

    def platform_slug(self) -> str:
        """dcim/devices/platform/slug.

        :return: Platform slug.

        :raise NbParserError: if device has no: hostname, version platform.
        """
        strict_actual = self.strict
        self.strict = True
        _ = self.is_dcim("devices")
        _ = self.primary_ip4()
        device_type = self.platform_name()
        required: str = string.ascii_lowercase + "_-"
        chars_invalid: LStr = [s for s in device_type if s not in required]
        if chars_invalid:
            device_type = super().platform_slug()
        device_type = device_type.replace("-", "_")
        self.strict = strict_actual
        return device_type

    # ========================== custom values ===========================

    def firewalls__in_aggregate(self) -> SStr:
        """aggregates/custom_fields/ or description."""
        if hostnames := self._hosts_in_cf_firewalls():
            return hostnames
        if hostnames := self._hosts_in_aggr_descr():
            return hostnames
        return set()

    def _hosts_in_cf_firewalls(self) -> SStr:
        """Hostnames in aggregates/custom_fields/firewalls."""
        try:
            value = self.data["custom_fields"]["firewalls"]
        except (KeyError, TypeError):
            return set()
        if not value or not isinstance(value, str):
            return set()
        hostnames_ = "\n".join(vlist.split(value, ignore="_-"))
        hostnames = re.findall(r"^(\w+-\w+-\w+-\w+)", hostnames_, re.M)
        return set(hostnames)

    def _hosts_in_aggr_descr(self) -> SStr:
        """Hostnames in aggregates/description."""
        tags = self.tags()
        if "noc_aggregates_belonging" not in tags:
            return set()

        try:
            description = self.data["description"]
        except (KeyError, TypeError):
            if self.strict:
                raise
            return set()

        if not isinstance(description, str):
            if self.strict:
                raise TypeError(f"{description=}, {str} expected.")
            return set()

        descr_ = "\n".join(vlist.split(description, ignore="_-"))
        hostnames = set(re.findall(r"^(\w+-\w+-\w+-\w+)", descr_, re.M))
        return hostnames
