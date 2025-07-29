# pylint: disable=R0902,R0903

"""Core Forager."""

from nbforager.foragers.base_fa import BaseAF
from nbforager.foragers.forager import Forager
from nbforager.nb_api import NbApi
from nbforager.nb_tree import NbTree


class CoreAF(BaseAF):
    """Core Forager."""

    def __init__(self, api: NbApi, root: NbTree, tree: NbTree):
        """Init CoreAF.

        :param api: NbApi object, connector to Netbox API.
        :param root: NbTree object where raw data from Netbox needs to be saved.
        :param tree: NbTree object where transformed data from Netbox needs to be saved.
        """
        super().__init__(api, root, tree)
        self.data_files = self.DataFilesF(self)
        self.data_sources = self.DataSourcesF(self)
        self.jobs = self.JobsF(self)

    class DataFilesF(Forager):
        """DataFilesF."""

    class DataSourcesF(Forager):
        """DataSourcesF."""

    class JobsF(Forager):
        """JobsF."""
