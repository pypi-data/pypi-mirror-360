# pylint: disable=R0902,R0903

"""Wireless Forager."""

from nbforager.foragers.base_fa import BaseAF
from nbforager.foragers.forager import Forager
from nbforager.nb_api import NbApi
from nbforager.nb_tree import NbTree


class WirelessAF(BaseAF):
    """Wireless Forager."""

    def __init__(self, api: NbApi, root: NbTree, tree: NbTree):
        """Init WirelessAF.

        :param api: NbApi object, connector to Netbox API.
        :param root: NbTree object where raw data from Netbox needs to be saved.
        :param tree: NbTree object where transformed data from Netbox needs to be saved.
        """
        super().__init__(api, root, tree)
        self.wireless_lan_groups = self.WirelessLanGroupsF(self)
        self.wireless_lans = self.WirelessLansF(self)
        self.wireless_links = self.WirelessLinksF(self)

    class WirelessLanGroupsF(Forager):
        """WirelessLanGroupsF."""

    class WirelessLansF(Forager):
        """WirelessLansF."""

    class WirelessLinksF(Forager):
        """WirelessLinksF."""
