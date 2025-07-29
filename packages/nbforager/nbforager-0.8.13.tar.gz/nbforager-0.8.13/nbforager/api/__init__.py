"""api."""

from __future__ import annotations

from typing import Union

from nbforager.api.circuits import CircuitsAC
from nbforager.api.core import CoreAC
from nbforager.api.dcim import DcimAC
from nbforager.api.extras import ExtrasAC
from nbforager.api.ipam import IpamAC
from nbforager.api.tenancy import TenancyAC
from nbforager.api.users import UsersAC
from nbforager.api.virtualization import VirtualizationAC
from nbforager.api.wireless import WirelessAC

ConnectorA = Union[
    CircuitsAC,
    CoreAC,
    DcimAC,
    ExtrasAC,
    IpamAC,
    TenancyAC,
    UsersAC,
    VirtualizationAC,
    WirelessAC,
]
