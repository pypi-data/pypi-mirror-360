# pylint: disable=R0801,R0902,R0913,R0914,R0915

"""NbApi, Python wrapper of Netbox REST API."""

from __future__ import annotations

from typing import Callable

from requests import Response

from nbforager import helpers as h
from nbforager.api.circuits import CircuitsAC
from nbforager.api.connector import Connector, GConnector
from nbforager.api.core import CoreAC
from nbforager.api.dcim import DcimAC
from nbforager.api.extras import ExtrasAC
from nbforager.api.ipam import IpamAC
from nbforager.api.plugins_ca import PluginsAC
from nbforager.api.status import StatusC
from nbforager.api.tenancy import TenancyAC
from nbforager.api.users import UsersAC
from nbforager.api.virtualization import VirtualizationAC
from nbforager.api.wireless import WirelessAC
from nbforager.constants import APPS
from nbforager.parser.nb_parser import NbParser
from nbforager.types_ import ODLStr, ODDAny, DAny, LDAny, LStr, LT2Str


class NbApi:
    """NbApi, Python wrapper of Netbox REST API.

    It is a set of connectors to Netbox endpoints.
    Connectors are nested by principle ``{application}.{model}.{method}``,
    where:

    - **application** can be: ``circuits``, ``dcim``, ``ipam``, etc.;
    - **model** can be: ``circuit_terminations``, ``ip_addresses``, etc.;
    - **method** can be: ``create``, ``delete``, ``get``, ``update``.

    For example https://demo.netbox.dev/api/ipam/ip-addresses/
    can be reached by ``NbApi.ipam.ip_addresses.get()`` method.

    The parameters for the ``create``, ``delete``, ``update`` methods are
    identical in all models.
    The parameters for the ``get`` method are different for each model.
    Only ``NbApi.ipam.ip_addresses.get()`` is described in this documentation.
    Other models are implemented in a similar manner.
    Exact parameters you can find in `Schema`_.
    """

    def __init__(
        self,
        host: str,
        token: str = "",
        scheme: str = "https",
        port: int = 0,
        verify: bool = True,
        limit: int = 1000,
        url_length: int = 2047,
        # Multithreading
        threads: int = 1,
        interval: float = 0.0,
        # Errors processing
        timeout: int = 60,
        max_retries: int = 0,
        sleep: int = 10,
        strict: bool = False,
        # Settings
        extended_get: bool = True,
        default_get: ODDAny = None,
        loners: ODLStr = None,
        **kwargs,
    ):
        """Init NbApi.

        :param str host: Netbox host name.

        :param str token: Netbox token.

        :param str scheme: Access method: `https` or `http`. Default is `https`.

        :param int port: TCP port.
            Default is `443` for scheme=`https`, `80` for scheme=`http`.

        :param bool verify: Transport Layer Security.
            `True` - A TLS certificate required,
            `False` - Requests will accept any TLS certificate.
            Default is `True`.

        :param int limit: Split the query to multiple requests
            if the count of objects exceeds this value. Default is `1000`.

        :param int url_length: Split the query to multiple requests
            if the URL length exceeds maximum length due to a long list of
            GET parameters. Default is `2047`.

        :param int threads: Threads count. <=1 is loop mode, >=2 is threading mode.
            Default id `1`.

        :param float interval: Wait this time between the threading requests (seconds).
            Default is `0`. Useful to optimize session spikes and achieve
            script stability in Docker with limited resources.

        :param int timeout: Session timeout (seconds). Default is `60`.

        :param int max_retries: Retries the request multiple times if the Netbox API
            does not respond or responds with a timeout. Default is `0`. This is useful
            for scheduled scripts in cron jobs, when the connection to Netbox server is
            not stable.

        :param int sleep: Interval (seconds) before the next retry after
            session timeout reached. Default is `10`.

        :param bool strict: When querying objects by tag, if there are no tags present,
            the Netbox API response returns a status_code=400.
            True - ConnectionError is raised when status_code=400.
            False - WARNING message is logged and an empty list is returned with status_code=200.
            Default is `False`.

        :param bool extended_get: True - Extend filtering parameters in GET request,
            ``{parameter}`` can be used instead of ``{parameter}_id``. Default is `True`.

        :param dict default_get: Set default filtering parameters, to be used in each
            GET request.

        :param dict loners: Set :ref:`Filtering parameters in an OR manner`.

        Application/model connectors:

        :ivar obj circuits: :py:class:`.CircuitsAC` :doc:`CircuitsAC`.
        :ivar obj core: :py:class:`.CoreAC` :doc:`CoreAC`.
        :ivar obj dcim: :py:class:`.DcimAC` :doc:`DcimAC`.
        :ivar obj extras: :py:class:`.ExtrasAC` :doc:`ExtrasAC`.
        :ivar obj ipam: :py:class:`.IpamAC` :doc:`IpamAC`.
        :ivar obj plugins: :py:class:`.PluginsAC` :doc:`PluginsAC`.
        :ivar obj tenancy: :py:class:`.TenancyAC` :doc:`TenancyAC`.
        :ivar obj users: :py:class:`.UsersAC` :doc:`UsersAC`.
        :ivar obj virtualization: :py:class:`.VirtualizationAC` :doc:`VirtualizationAC`.
        :ivar obj wireless: :py:class:`.WirelessAC` :doc:`WirelessAC`.
        """
        kwargs = {
            "host": host,
            "token": token,
            "scheme": scheme,
            "port": port,
            "verify": verify,
            "limit": limit,
            "url_length": url_length,
            "threads": threads,
            "interval": interval,
            "timeout": timeout,
            "max_retries": max_retries,
            "sleep": sleep,
            "strict": strict,
            "extended_get": extended_get,
            "default_get": default_get,
            "loners": loners,
            **kwargs,
        }
        # application connectors
        self.circuits = CircuitsAC(**kwargs)
        self.core = CoreAC(**kwargs)
        self.dcim = DcimAC(**kwargs)
        self.extras = ExtrasAC(**kwargs)
        self.ipam = IpamAC(**kwargs)
        self.plugins = PluginsAC(**kwargs)
        self.status = StatusC(**kwargs)  # connector
        self.tenancy = TenancyAC(**kwargs)
        self.users = UsersAC(**kwargs)
        self.virtualization = VirtualizationAC(**kwargs)
        self.wireless = WirelessAC(**kwargs)

    def __repr__(self) -> str:
        """__repr__."""
        name = self.__class__.__name__
        return f"<{name}: {self.host}>"

    def __copy__(self) -> NbApi:
        """Create a duplicate of the object.

        :return: A copy of the current object.
        """
        connector = self.circuits.circuit_terminations
        return type(self)(
            host=connector.host,
            token=connector.token,
            scheme=connector.scheme,
            port=connector.port,
            verify=connector.verify,
            limit=connector.limit,
            url_length=connector.url_length,
            threads=connector.threads,
            interval=connector.interval,
            timeout=connector.timeout,
            max_retries=connector.max_retries,
            sleep=connector.sleep,
            strict=connector.strict,
            extended_get=connector.extended_get,
            default_get=connector.default_get,
            loners=connector.loners,
        )

    # ============================= property =============================

    @property
    def host(self) -> str:
        """Netbox host name."""
        return self.circuits.circuit_terminations.host

    @property
    def url(self) -> str:
        """Netbox base URL."""
        return self.circuits.circuit_terminations.url_base

    @property
    def threads(self) -> int:
        """Threads count."""
        return self.circuits.circuit_terminations.threads

    @threads.setter
    def threads(self, threads: int) -> None:
        """Set the number of threads.

        :param threads: Threads count to set.

        :return: None. Update threads in all connectors.
        """
        for app in self.apps():
            models: LStr = [s for s in dir(getattr(self, app)) if s[0].islower()]
            for model in models:
                connector = getattr(getattr(self, app), model)
                setattr(connector, "threads", threads)

    # ============================= methods ==============================

    @staticmethod
    def apps() -> LStr:
        """Get list of application names.

        :return: Applications.
        :rtype: List[str]
        """
        return list(APPS)

    def app_models(self) -> LT2Str:
        """Get list of application model names.

        :return: Application model names.
        :rtype: List[Tuple[str, str]]
        """
        app_models: LT2Str = []
        for app in self.apps():
            models: LStr = [s for s in dir(getattr(self, app)) if s[0].islower()]
            for model in models:
                app_models.append((app, model))
        return app_models

    def app_paths(self) -> LStr:
        """Get list of application/model paths.

        :return: Application/model paths.
        :rtype: List[str]
        """
        app_paths: LStr = []
        for app in self.apps():
            models: LStr = [s for s in dir(getattr(self, app)) if s[0].islower()]
            for model in models:
                connector = getattr(getattr(self, app), model)
                path = getattr(connector, "path")
                path = path.rstrip("/")
                app_paths.append(path)
        return app_paths

    def connectors(self) -> GConnector:
        """Return generator of Connector instances ordered based on dependencies.
            Connectors to models with the lowes count of dependencies will be first.

        :return: Generator of Connector instances.
        """
        paths: LStr = h.dependency_ordered_paths()
        for path in paths:
            app, model = h.path_to_attrs(path)
            connector: Connector = getattr(getattr(self, app), model)
            yield connector

    def copy(self, **kwargs) -> NbApi:
        """Create a duplicate of the object.

        :param kwargs: Keyword arguments to replace in original object.
        :return: A copy of the current object.
        """
        connector = self.circuits.circuit_terminations
        params: DAny = {
            "host": connector.host,
            "token": connector.token,
            "scheme": connector.scheme,
            "port": connector.port,
            "verify": connector.verify,
            "limit": connector.limit,
            "url_length": connector.url_length,
            "threads": connector.threads,
            "interval": connector.interval,
            "timeout": connector.timeout,
            "max_retries": connector.max_retries,
            "sleep": connector.sleep,
            "strict": connector.strict,
            "extended_get": connector.extended_get,
            "default_get": connector.default_get,
            "loners": connector.loners,
        }
        params.update(kwargs)
        return type(self)(**params)

    def get(self, **kwargs) -> LDAny:
        """Get an objects in Netbox using the app/model in the provided URL.

        :param kwargs: Parameters of object, only URL is required.

        :return: List of dictionaries containing Netbox objects.
        :rtype: List[dict]
        """
        url = str(kwargs.get("url") or "")
        app, model, id_ = h.url_to_ami(url)
        params = {"id": id_} if id_ else {}
        method: Callable = getattr(getattr(getattr(self, app), model), "get")
        return method(**params)

    def get_d(self, **kwargs) -> DAny:
        """Get an objects in Netbox using the app/model in the provided URL.

        :param kwargs: Parameters of object, only URL with ID is required.

        :return: Dictionary containing Netbox object.
        :rtype: dict
        """
        url = str(kwargs.get("url") or "")
        app, model, id_ = h.url_to_ami(url)
        if not id_:
            raise ValueError("ID is required in the URL.")
        method: Callable = getattr(getattr(getattr(self, app), model), "get")
        if objects := method(id=id_):
            return objects[0]
        return {}

    def create(self, **kwargs) -> Response:
        """Create an object in Netbox using the app/model in the provided URL.

        :param kwargs: Parameters for creating a new object.
        The `url` and `id` parameters will be ignored.

        :return: Session response.

            - <Response [201]> Object successfully created,
            - <Response [400]> Object already exist.
        :rtype: Response
        """
        url = str(kwargs.get("url") or "")
        app, model, _ = h.url_to_ami(url)
        data: DAny = {k: v for k, v in kwargs.items() if k not in ["url", "id"]}
        method: Callable = getattr(getattr(getattr(self, app), model), "create")
        return method(**data)

    def create_d(self, **kwargs) -> DAny:
        """Create an object in Netbox using the app/model in the provided URL.

        :param kwargs: Parameters for creating a new object.
        The `url` and `id` parameters will be ignored.

        :return: Data of newly created object.
        :rtype: dict
        """
        url = str(kwargs.get("url") or "")
        app, model, _ = h.url_to_ami(url)
        data: DAny = {k: v for k, v in kwargs.items() if k not in ["url", "id"]}
        method: Callable = getattr(getattr(getattr(self, app), model), "create_d")
        return method(**data)

    def delete(self, **kwargs) -> Response:
        """Delete an object from Netbox using the ID in the provided URL.

        :param kwargs: Parameters of object to delete. Only url to object is required.
        :return: Session response.

            - <Response [204]> Object successfully deleted,
            - <Response [404]> Object not found.
        :rtype: Response
        """
        url = str(kwargs.get("url") or "")
        app, model, idx = h.url_to_ami(url)
        method: Callable = getattr(getattr(getattr(self, app), model), "delete")
        return method(id=idx)

    # noinspection PyIncorrectDocstring
    def update(self, **kwargs) -> Response:
        """Update an object in Netbox using the app/model in the provided URL.

        :param id: Netbox object id to update.
        :type id: int

        :param kwargs: Parameters to update an object in Netbox.

        :return: Session response.

            - <Response [200]> Object successfully updated,
            - <Response [400]> Invalid data.
        :rtype: Response
        """
        url = str(kwargs.get("url") or "")
        app, model, idx = h.url_to_ami(url)
        data: DAny = {k: v for k, v in kwargs.items() if k not in ["url"]}
        data["id"] = idx
        method: Callable = getattr(getattr(getattr(self, app), model), "update")
        return method(**data)

    def version(self) -> str:
        """Get Netbox version.

        :return: Netbox version, if version >= 3, otherwise empty string.
        """
        status_d: DAny = self.status.get()
        version = NbParser(status_d).str("netbox-version")
        return version
