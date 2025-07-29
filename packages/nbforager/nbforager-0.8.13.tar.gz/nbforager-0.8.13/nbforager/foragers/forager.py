# pylint: disable=R0801,R0902

"""Base for Foragers."""

from __future__ import annotations

import time
from queue import Queue
from threading import Thread
from urllib.parse import urlparse, parse_qs

from vhelpers import vstr

from nbforager import helpers as h
from nbforager import nb_tree
from nbforager.nb_api import NbApi
from nbforager.nb_tree import NbTree
from nbforager.parser import nb_parser
from nbforager.types_ import LDAny, DiDAny, LStr, LT2StrDAny, DList, LDList, SInt, DAny


class Forager:
    """Forager methods for different models."""

    def __init__(self, forager_a):
        """Init Forager.

        :param forager_a: Parent forager.
        :type forager_a: CircuitsF or DcimF or IpamF or TenancyF
        """
        app = h.attr_name(forager_a)
        model = h.attr_name(self)
        self.app = app
        self.model = model
        self.api: NbApi = forager_a.api
        self.connector = getattr(getattr(self.api, app), model)
        # data
        self.root: NbTree = forager_a.root
        self.root_d: DiDAny = getattr(getattr(self.root, app), model)
        self.tree: NbTree = forager_a.tree
        self.tree_d: DiDAny = getattr(getattr(self.tree, app), model)

    def __repr__(self) -> str:
        """__repr__."""
        name = self.__class__.__name__
        params = vstr.repr_info(self.count())
        return f"<{name}: {params}>"

    # ============================= property =============================

    @property
    def interval(self) -> int:
        """Wait this time between requests (seconds)."""
        return self.connector.interval

    @property
    def threads(self) -> int:
        """Threads count."""
        return self.connector.threads

    # ============================= methods ==============================

    def count(self) -> int:
        """Count of the Netbox objects in the NbForager.root.{model}.

        :return: Count of the Netbox objects.

        :rtype: int
        """
        return len(self.root_d)

    # noinspection PyProtectedMember
    def get(self, nested: bool = False, **kwargs) -> None:
        """Retrieve data from the Netbox.

        Request data based on the filter parameters (kwargs described in the
        NbApi connector) and save to the NbForager.root.

        :param bool nested: `True` - Request base and nested objects,
            `False` - Request only base objects. Default id `False`

        :param kwargs: Filtering parameters.

        :return: None. Update self object.
        """
        # Query main data
        kwargs_: DAny = self._delete_existing_nested_ids(**kwargs)
        if kwargs and not kwargs_:
            return
        nb_objects: LDAny = self._get_root_data_from_netbox(nested=nested, **kwargs_)
        if not nested:
            return
        urls: LStr = self._collect_nested_urls(nb_objects)

        # Query nested data
        # threads
        results: LDAny = []
        if self.threads > 1:
            path_params: LT2StrDAny = self._get_path_params(urls)
            self._clear_connector_results(path_params)
            self._query_threads(path_params)
            results_: LDAny = self._pop_connector_results(path_params)
            results.extend(results_)

        # loop
        else:
            for url in urls:
                app, model, _ = h.url_to_ami_items(url)
                path = f"{app}/{model}/"
                connector = self._get_connector(path)
                params_d: DList = parse_qs(urlparse(url).query)
                params_ld: LDList = connector._validate_params(**params_d)  # pylint: disable=W0212

                # slice params
                params_ld = h.slice_params_ld(
                    url=url,
                    max_len=connector.url_length,
                    keys=connector._slices,  # pylint: disable=W0212
                    params_ld=params_ld,
                )

                for params_d in params_ld:
                    results_ = connector._query_loop(path, params_d)  # pylint: disable=W0212
                    results.extend(results_)

        self._save_results(results)

    def find_root(self, **kwargs) -> LDAny:
        """Find Netbox objects in NbForager.root by extended finding parameters.

        :param kwargs: Extended filtering parameters.
            Different parameters work like an ``AND`` operator.
            Different values of the same parameter work like an ``OR`` operator.
            Parameters with double underscores ``__`` will be split into a list of keys.

        :return: Filtered Netbox objects.
        """
        return nb_parser.find_objects(objects=list(self.root_d.values()), **kwargs)

    def find_rse(self, role: str = "", site: str = "", env: str = "", **kwargs) -> LDAny:
        """Find Netbox objects in NbForager.tree by Role-Sile-Env finding parameters.

        This method used in a specific project to simplify prefixes search.

        :param role: ipam/role/slug value.
        :param site: ipam/sile/slug value.
        :param env: custom_fields/env value.
        :param kwargs: Role-Sile-Env filtering parameters.

        :return: Filtered Netbox objects.
        """
        params = {
            "role__slug": str(role),
            "site__slug": str(site),
            "custom_fields__env": str(env),
        }
        params = {k: v for k, v in params.items() if v}
        kwargs.update(params)
        return nb_parser.find_objects(objects=list(self.tree_d.values()), **kwargs)

    def find_tree(self, **kwargs) -> LDAny:
        """Find Netbox objects in NbForager.tree by extended finding parameters.

        :param kwargs: Extended filtering parameters.
            Different parameters work like an ``AND`` operator.
            Different values of the same parameter work like an ``OR`` operator.
            Parameters with double underscores ``__`` will be split into a list of keys.

        :return: Filtered Netbox objects.
        """
        return nb_parser.find_objects(objects=list(self.tree_d.values()), **kwargs)

    # ============================= helpers ==============================

    def _delete_existing_nested_ids(self, **kwargs) -> DAny:
        """Delete the IDs of objects that are already present in the tree and nested=True.

        Delete only if kwargs["id"] is a list, ignore other data types.

        :param kwargs: Filtering parameters.

        :return: None. Update IDs in kwargs.
        """
        if list(kwargs) != ["id"]:
            return kwargs
        if not isinstance(kwargs["id"], list):
            return kwargs
        ids: SInt = set(kwargs["id"])
        existing_ids: SInt = {d["id"] for d in self.find_root(_nested=True, **kwargs)}
        if new_ids := sorted(set(ids).difference(existing_ids)):
            return {"id": new_ids}
        return {}

    def _get_root_data_from_netbox(self, nested: bool = False, **kwargs) -> LDAny:
        """Retrieve data from the Netbox.

        Request data based on the kwargs filter parameters and
        save the received objects to the NbForager.root.
        Set extra `_nested` value in Netbox object.

        :param bool nested: `True` - Request base and nested objects,
            `False` - Request only base objects. Default id `False`

        :param kwargs: Filtering parameters.

        :return: List of Netbox objects. Update NbForager.root object.
        """
        nb_objects: LDAny = self.connector.get(**kwargs)
        for nb_object in nb_objects:
            nb_object["_nested"] = nested
            idx = int(nb_object["id"])
            self.root_d[idx] = nb_object
        return nb_objects

    def _collect_nested_urls(self, nb_objects: LDAny) -> LStr:
        """Collect nested urls.

        :param nb_objects: List of Netbox objects.

        :return: Nested URLs.
        """
        urls: LStr = h.nested_urls(nb_objects)
        urls = nb_tree.missed_urls(urls=urls, tree=self.root)
        urls = h.join_urls(urls)
        urls = [s for s in urls if h.url_to_ami_items(s)[0]]

        urls_: LStr = []

        for url in urls:
            app, model, _ = h.url_to_ami_items(url)
            path = f"{app}/{model}/"
            connector = self._get_connector(path)
            urls_sliced = h.slice_url(url, max_len=connector.url_length)
            urls_.extend(urls_sliced)

        return urls_

    # noinspection PyProtectedMember
    def _get_path_params(self, urls: LStr) -> LT2StrDAny:
        """Get path of app/model and parameters based on the list of URLs.

        :param urls: A list of URLs.

        :return: A list of tuples containing the path and parameters.
        """
        path_params: LT2StrDAny = []
        for url in urls:
            app, model, _ = h.url_to_ami_items(url)
            path = f"{app}/{model}/"
            connector = self._get_connector(path)
            params_d = parse_qs(urlparse(url).query)
            params_ld: LDAny = h.slice_params_ld(
                url=connector.url,
                max_len=connector.url_length,
                keys=connector._slices,  # pylint: disable=W0212
                params_ld=[params_d],
            )
            for params_d in params_ld:
                path_params.append((path, params_d))
        return path_params

    # noinspection PyProtectedMember
    def _clear_connector_results(self, path_params: LT2StrDAny) -> None:
        """Clear results in connectors by path app/model."""
        for path, _ in path_params:
            connector = self._get_connector(path)
            connector._results.clear()  # pylint: disable=W0212

    def _query_threads(self, path_params: LT2StrDAny) -> None:
        """Retrieve data from Netbox in threaded mode.

        :param path_params: A list of tuples containing the path app/model and parameters.

        :return: None. Save results to self._results.
        """
        queue: Queue = Queue()
        for path, params_d in path_params:
            queue.put((path, params_d))

        for idx in range(self.threads):
            if self.interval:
                time.sleep(self.interval)
            thread = Thread(name=f"Thread-{idx}", target=self._run_queue, args=(queue,))
            thread.start()
        queue.join()

    # noinspection PyProtectedMember
    def _run_queue(self, queue: Queue) -> None:
        """Process tasks from the queue.

        This method dequeues and executes tasks until the queue is empty.
        Each task is expected to be a callable method with its corresponding params_d parameters.
        :param queue: A queue containing path app/model and parameters pairs to be requested.

        :return: None. Update connector._results list.
        """
        while not queue.empty():
            path, params_d = queue.get()
            connector = self._get_connector(path)
            connector._query_data_thread(path=path, params_d=params_d)  # pylint: disable=W0212
            queue.task_done()

    # noinspection PyProtectedMember
    def _pop_connector_results(self, path_params: LT2StrDAny) -> LDAny:
        """Get results from connectors by path app/model and delete cached results."""
        results: LDAny = []
        for path, _ in path_params:
            connector = self._get_connector(path)
            results.extend(connector._results)  # pylint: disable=W0212
            connector._results.clear()  # pylint: disable=W0212
        return results

    def _get_connector(self, path: str):
        """Get connector by app/model path.

        :param path: The app/model path.

        :return: The connector object.

        :rtype:  DeviceRolesC or DeviceTypesC or LocationsC or RacksC or etc.
        """
        app, model = h.path_to_attrs(path)
        connector = getattr(getattr(self.api, app), model)
        return connector

    def _save_results(self, results: LDAny) -> None:
        """Save Netbox objects to root NbTree object.

        :param results: Data to be saved.
        :return: None. root NbTree object.
        """
        for data in results:
            app, model, idx_ = h.url_to_ami_items(data["url"])
            idx = int(idx_)
            path = f"{app}/{model}"
            model_d: DiDAny = self._get_root_data(path)
            if idx not in model_d:
                data["_nested"] = False
                model_d[idx] = data

    def _get_root_data(self, path: str) -> DiDAny:
        """Get data in self root by app/model path.

        :param path: The app/model path.

        :return: The model data.
        """
        app, model = h.path_to_attrs(path)
        data = getattr(getattr(self.root, app), model)
        return data
