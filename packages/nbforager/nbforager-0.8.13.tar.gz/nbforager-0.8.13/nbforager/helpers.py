"""Helper functions."""

import itertools
import urllib
from copy import deepcopy
from typing import Any
from urllib.parse import ParseResult, urlencode, urlparse, parse_qs

from vhelpers import vlist, vparam, vint

from nbforager.exceptions import NbApiError
from nbforager.constants import DEPENDENT_MODELS
from nbforager.types_ import LStr, LDAny, DDDLInt, LValue, LParam, LDList, DList, DLStr, ODLStr
from nbforager.types_ import LTInt2, DAny, SeqStr, SStr, TValues, TLists, T2Str, T3Str, T3StrInt


def dependency_ordered_paths(dependency: ODLStr = None) -> LStr:
    """Order paths based on dependencies. Models with the lowes count of dependencies will be first.

    :param dependency: Dictionary representing dependencies,
        where key is the parent model and value is a list of child models.
    :return: Ordered paths based on dependencies.
    :raises ValueError: If circular dependency, too many iterations.
    """
    paths: LStr = []

    idx = 0
    dependency_: DLStr = dependency if dependency else DEPENDENT_MODELS
    dependency_ = deepcopy(dependency_)

    while dependency_:
        for parent, children in dependency_.items():
            if parent in paths:
                continue
            diff = set(children).difference(set(paths))
            if parent == "dcim/devices":
                diff.discard("dcim/virtual-chassis")
            if not diff:
                paths.append(parent)

        dependency_ = {k: v for k, v in dependency_.items() if k not in paths}
        if not dependency_:
            break

        idx += 1
        if idx >= 100:
            raise ValueError("Circular dependency, too many iterations")

    return paths


# =========================== app model id ===========================


def am_to_object_type(app: str, model: str) -> str:
    """Convert application and model to object_type.

    :param app: Application value.
    :param model: Model value.
    :return: Object type.

    :example:
        am_to_object_type("ipam", "ip-address") -> "ipam.ipaddress"
    """
    model_singular = plural_to_singular(model)
    if app == "virtualization":
        if model_singular == "interface":
            model_singular = f"vm{model_singular}"
    return f"{app}.{model_singular}"


def attr_name(obj: Any) -> str:
    """Transform the class name to the attribute name, lowercase without postfix.

    :param obj: The object or name to transform.

    :return: Attribute name.

    :example:
        attr_name("TenantGroupsJ") -> "tenant_groups"
    """
    name = obj.__class__.__name__
    if isinstance(obj, str):
        name = obj
    name = replace_upper(name)
    if name[:-1].endswith("_"):
        name = name[:-2]
        if name[:-1].endswith("_"):
            name = name[:-2]
    return name


def attr_names(obj: Any) -> LStr:
    """Transform the class names to the attribute names, lowercase without postfix.

    :param obj: The object or name to transform.

    :return: Attribute names.

    :example:
        attr_names(NbForager.tenancy) -> ["tenant_groups", "tenants"]
    """
    attrs = [s for s in dir(obj) if s[0].isupper()]
    methods = [replace_upper(s)[:-2] for s in attrs]
    return methods


def attr_to_model(attr: str) -> str:
    """Convert attribute name to model name.

    :param attr: The attribute name to be converted.

    :return: The converted model name.

    :example:
        attr_to_model("ip_addresses") -> "ip-addresses"
    """
    return attr.replace("_", "-")


def join_urls(urls: LStr) -> LStr:
    """Join URLs by models with list of IDs in query.

    :param urls: A list of URLs to be joined.

    :return: A list of joined URLs.

    :example:
        urls = ["https://domain.com/api/ipam/vrfs/1", "https://domain.com/api/ipam/vrfs/2"]
        join_urls(urls) -> ["https://domain.com/api/ipam/vrfs?id=1&id=2"]
    """
    items = []
    for url in sorted(urls):
        url_l = url.split("/")
        url_base = "/".join(url_l[:-3])
        app, model, digit = url_l[-3:]
        item = (url_base, app, model, digit)
        items.append(item)

    # create dict
    data_uam: DDDLInt = {}
    for url_base, app, model, _ in items:
        data_uam.setdefault(url_base, {}).setdefault(app, {}).setdefault(model, [])

    # append ids
    for url_base, app, model, digit in items:
        data_uam[url_base][app][model].append(int(digit))

    # join urls
    urls_: LStr = []
    for url_base, data_am in data_uam.items():
        for app, data_m in data_am.items():
            for model, ids in data_m.items():
                params = urlencode({"id": sorted(set(ids))}, doseq=True)
                url = f"{url_base}/{app}/{model}?{params}"
                urls_.append(url)
    return urls_


def model_to_attr(model: str) -> str:
    """Convert model name to attribute name.

    :param model: The model name to be converted.

    :return: The converted attribute name.

    :example:
        model_to_attr("ip-addresses") -> "ip_addresses"
    """
    return model.replace("-", "_")


def nested_urls(nb_objects: LDAny) -> LStr:
    """Get a list of URLs from a Netbox nested objects.

    :param nb_objects: A list of Netbox objects.

    :return: URLs of nested objects.
    """
    urls: LStr = []
    for nb_object in nb_objects:
        if not isinstance(nb_object, dict):
            continue
        for key, value in nb_object.items():
            if key == "url" and isinstance(value, str):
                urls.append(value)
            elif isinstance(value, list):
                urls_ = nested_urls(value)
                urls.extend(urls_)
            elif isinstance(value, dict):
                if url := value.get("url"):
                    if isinstance(url, str):
                        urls.append(url)
    urls = vlist.no_dupl(urls)
    return sorted(urls)


def path_to_attrs(path: str) -> T2Str:
    """Convert path of app/model to attribute names.

    :param path: Path of app/model.

    :return: Application and model attribute names.

    :example:
        path_to_attrs("ipam/ip-addresses") -> "ipam", "ip_addresses"
    """
    app, model = path.strip("/").split("/")
    model = model_to_attr(model)
    return app, model


def plural_to_singular(plural: str) -> str:
    """Convert a plural model name to a singular model name.

    :param plural: A plural model name.
    :return: A singular model name.
    """
    singular = plural.replace("_", "").replace("-", "")
    if singular.endswith("ies"):
        singular = singular[:-3] + "y"  # entries -> entry
    elif singular.endswith("ses"):
        singular = singular[:-2]  # ipaddresses -> ipaddress
    elif singular.endswith("xes"):
        singular = singular[:-2]  # prefixes -> prefix
    elif singular.endswith("sis"):
        pass  # chassis -> chassis
    elif singular.endswith("s"):
        singular = singular[:-1]  # types -> type
    return singular


def replace_upper(word: str) -> str:
    """Replace upper character with underscore and lower.

    :param word: The word to be modified.

    :return: The modified word.

    :example: replace_upper("IpAddresses") -> "ip_addresses"
    """
    if not word:
        return ""
    word = word[0].lower() + word[1:]
    new_word = ""
    for char in word:
        if char.isupper():
            new_word += "_" + char.lower()
        else:
            new_word += char
    return new_word


def url_to_ami_items(url: str) -> T3Str:
    """Split the URL into the application, model, and ID items.

    :param url: The URL to be parsed.

    :return: A tuple containing the application, model, and port (if available).
             If the URL is invalid or does not contain the necessary items, returns empty strings.

    :example:
        split_url("https://domain.com/api/ipam/vrfs?id=1") -> ("ipam", "vrfs", "1")
    """
    url_o: ParseResult = urllib.parse.urlparse(url)
    if not url_o.path:
        return "", "", ""

    path = url_o.path.strip("/")
    items = path.split("/")
    if len(items) < 2:
        return "", "", ""
    if items[0] == "api":
        items = items[1:]
    if len(items) < 2 or len(items) > 3:
        return "", "", ""

    app = str(items[0])
    model = str(items[1])
    id_ = ""
    if len(items) == 3:
        id_ = str(items[2])
    return app, model, id_


def url_to_ami(url: str, path: bool = False) -> T3StrInt:
    """Convert URL of app/model/id to attribute names.

    :param url: URL of app/model/id.
    :param path: If True, return model as item of path, else return madel as attribute.
    :return: Tuple of application attribute name, model attribute name and object ID.

    :example:
        url_to_attrs("https://domain.com/api/ipam/ip-addresses/1") -> "ipam", "ip_addresses", 1
    """
    app, model, idx = url_to_ami_items(url)

    while True:
        if app and not app.isdigit():
            if model and not model.isdigit():
                if not idx or idx.isdigit():
                    break
        raise NbApiError(f"Invalid {url=}, expected app/modem/id format.")

    if not path:
        model = model_to_attr(model)

    return app, model, vint.to_int(idx)


def url_to_am_path(url: str) -> str:
    """Convert URL to path app/model.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the app/mode/ path.

    :example:
        url_to_am_path("https://domain.com/api/ipam/vrf/1") -> "ipam/vrf/"
    """
    app, model, _ = url_to_ami_items(url)
    if not (app and model):
        raise ValueError(f"{app=} {model=} required.")
    return f"{app}/{model}/"


def url_to_ami_path(url: str) -> str:
    """Convert URL to path app/model/id.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the app/mode/id path.

    :example:
        url_to_am_path("https://domain.com/api/ipam/vrf/1") -> "ipam/vrf/1/"
    """
    app, model, id_ = url_to_ami_items(url)
    if not (app and model and id_):
        raise ValueError(f"{app=} {model=} {id_=} required.")
    return f"{app}/{model}/{id_}/"


def url_to_ami_url(url: str) -> str:
    """Convert URL to short URL with /api/app/model/id.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the short URL.

    :example:
        url_to_ami_url("https://domain.com/api/ipam/vrf/1/") -> "/api/ipam/vrf/1/"
    """
    app, model, id_ = url_to_ami(url=url, path=True)
    ami_url = f"/api/{app}/{model}/"
    if id_:
        ami_url += f"{id_}/"
    return ami_url


def url_to_api_url(url: str) -> str:
    """Convert Netbox UI URl to API URL.

    :param url: A string representing the Netbox UI URL.
    :return: A string representing the Netbox API URL.

    :example:
        url_to_ui_url("https://domain.com/ipam/vrf/1/") -> "https://domain.com/api/ipam/vrf/1/"
    """
    url_o: ParseResult = urllib.parse.urlparse(url)
    app, model, id_ = url_to_ami(url=url, path=True)
    ui_url = f"{url_o.scheme}://{url_o.netloc}/api/{app}/{model}/"
    if id_:
        ui_url += f"{id_}/"
    return ui_url


def url_to_object_type(url: str) -> str:
    """Convert url to object_type.

    :param url: URL to Netbox object.
    :return: Object type.

    :example:
        url_to_object_type("/api/ipam/ip-addresses/1/") -> "ipam.ipaddress"
    """
    app, model, _ = url_to_ami(url)
    object_type = am_to_object_type(app, model)
    return object_type


def url_to_ui_url(url: str) -> str:
    """Convert Netbox API URl to UI URL.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the Netbox UI URL.

    :example:
        url_to_ui_url("https://domain.com/api/ipam/vrf/1/") -> "https://domain.com/ipam/vrf/1/"
    """
    url_o: ParseResult = urllib.parse.urlparse(url)
    app, model, id_ = url_to_ami(url=url, path=True)
    ui_url = f"{url_o.scheme}://{url_o.netloc}/{app}/{model}/"
    if id_:
        ui_url += f"{id_}/"
    return ui_url


# ============================== params ==============================


def join_params(params_ld: LDList, default_get: DList) -> LDList:
    """Join params_ld and default filtering parameters.

    :param params_ld: Filtering parameters.
    :param default_get: Default filtering parameters.
    :return: Joined filtering parameters.
    """
    if not params_ld:
        if not default_get:
            return []
        return [default_get.copy()]

    params_ld_: LDList = []
    for params_d in params_ld.copy():
        if not params_d:
            continue
        default_d = {k: v for k, v in default_get.items() if k not in params_d}
        params_d.update(default_d)
        params_ld_.append(params_d)
    return params_ld_


def make_combinations(need_split: SeqStr, params_d: DList) -> LDList:
    """Split the parallel parameters from the kwargs dictionary to valid combinations.

    Need to be split predefined in the need_split list and boolean values in params_d.
    :param need_split: Parameters that need to be split into different requests.
    :param params_d: A dictionary of keyword arguments.
    :return: A list of dictionaries containing the valid combinations.
    """
    keys_need_split = _get_keys_need_split(need_split, params_d)
    no_need_split_d = {k: v for k, v in params_d.items() if k not in keys_need_split}

    key_no_need_split = ""
    need_split_d: DList = {}
    for key, values in params_d.items():
        if key in keys_need_split:
            for value in values:
                need_split_d.setdefault(key, []).append({key: [value]})
        else:
            key_no_need_split = key

    params_l = list(need_split_d.values())
    if key_no_need_split:
        params_l.append([no_need_split_d])

    params_ld: LDList = []
    combinations = list(itertools.product(*params_l))
    for combination in combinations:
        params_d_ = {}
        for param_d_ in combination:
            params_d_.update(param_d_)
        if params_d_:
            params_ld.append(params_d_)
    return params_ld


def change_params_or(params_ld: LDList) -> LDList:
    """Change ``parameter`` with name ``or_{parameter}``.

    :param params_ld: Parameters that need to update.
    :return: Updated parameters.
    """
    params_ld_: LDList = []
    for params_d in params_ld:
        params_d_: DList = {}
        for name, values in params_d.items():
            if name.startswith("or_"):
                name = name.replace("or_", "", 1)
            params_d_[name] = values
        params_ld_.append(params_d_)
    return params_ld_


def _get_keys_need_split(need_split: SeqStr, params_d: DList) -> SStr:
    """Get keys that need to be split.

    :param need_split: Parameters that need to be split into different requests.
    :param params_d: A dictionary of keyword arguments.
    :return: Keys that need to be split.
    """
    keys_need_split: SStr = set()

    keys = list(params_d)
    while keys:
        key = keys.pop(0)
        # predefined
        for need_split_ in need_split:
            if key == need_split_:
                keys_need_split.add(key)
                break
        # or_{parameter}
        if key.startswith("or_"):
            keys_need_split.add(key)

    return keys_need_split


def generate_slices(url: str, max_len: int, key: str, values: LValue) -> LTInt2:
    """Generate start and end indexes of parameters, ready for URL slicing.

    :param url: URL that need to split.
    :param max_len: Maximum length of URL.
    :param key: The key of the parameter that needs to be sliced.
    :param values: The values of the parameter that need to be sliced.

    :return: The start and end indexes of the parameters, ready for URL slicing.
    """
    if len(values) <= 1:
        return [(0, 1)]

    slices: LTInt2 = []
    start = 0
    for idx in range(1, len(values) + 1):
        end_ = idx + 1
        params_ = [(key, s) for s in values[start:end_]]
        url_full = f"{url}&{urlencode(params_)}"
        if end_ < len(values) + 1:  # if value is not last
            if len(url_full) < max_len:  # if url is short
                continue  # increase length
        slices.append((start, idx))
        start = idx
    return slices


def slice_params_d(url: str, max_len: int, key: str, params_d: DList) -> LDList:
    """Generate sliced parameters, ready for URLs with valid length.

    If the length of the URL exceeds maximum allowed (due to a large number of parameters),
    then need split (slice) the request into multiple parts.
    :param url: URL that need to split.
    :param max_len: Maximum length of URL.
    :param key: The key of the parameter that needs to be sliced.
    :param params_d: Filter parameters, where one of key/value need be sliced.

    :return: Sliced parameters.

    :example:
        slice_params_d(max_len=50, params_d={"address": ["10.0.0.1", "10.0.0.2"], "family": 4}) ->
        [{"address": ["10.0.0.1"], "family": 4}, {"address": ["10.0.0.2"], "family": 4}]
    """
    values: LValue = _validate_values(values=params_d[key])
    params_common: LParam = [(k, v) for k, v in params_d.items() if k != key]
    params_w_offset: LParam = [*params_common, ("offset", 1000), ("limit", 1000)]

    slices: LTInt2 = generate_slices(
        url=f"{url}?{urlencode(params_w_offset)}",
        max_len=max_len,
        key=key,
        values=values,
    )

    params_sliced: LDList = []
    for start, end in slices:
        params_i = [(key, s) for s in values[start:end]]
        params_sliced_: DList = vparam.to_dict([*params_common, *params_i])
        params_sliced.append(params_sliced_)
    return params_sliced


def slice_params_ld(url: str, max_len: int, keys: LStr, params_ld: LDList) -> LDList:
    """Split params into different lists if slicing is required.

    :param url: URL that need to split.
    :param max_len: Maximum length of URL.
    :param keys: The keys of the parameters that could be sliced.
    :param params_ld: A list of parameters.

    :return: A list of sliced parameters.
    """
    params_ld_: LDList = []

    for params_d in params_ld:
        # no need slice
        key_of_long_value = get_key_of_longest_value(params_d)
        if not key_of_long_value:
            params_ld_.append(params_d)
            continue

        # no need slice
        if key_of_long_value not in keys:
            params_ld_.append(params_d)
            continue

        # need slice
        params_sliced: LDList = slice_params_d(
            url=url,
            max_len=max_len,
            key=key_of_long_value,
            params_d=params_d,
        )
        params_ld_.extend(params_sliced)

    if not params_ld_:
        params_ld_ = [{}]

    return params_ld_


def slice_url(url: str, max_len: int) -> LStr:
    """Split (slice) URL to multiple URLs if length is greater than max_len.

    :param url: URL that need to split.
    :param max_len: Maximum length of URL.

    :return: Sliced URLs.
    """
    url_o: ParseResult = urlparse(url)
    url_base = f"{url_o.scheme}://{url_o.netloc}{url_o.path}"
    query_s: str = urlparse(url).query
    params_d: DLStr = parse_qs(query_s)
    key = get_key_of_longest_value(params_d)
    values: LValue = _validate_values(values=params_d[key])
    params_common: LParam = [(k, v) for k, v in params_d.items() if k != key]
    params_w_offset = [*params_common, ("offset", 1000), ("limit", 1000)]

    slices: LTInt2 = generate_slices(
        url=f"{url_base}?{urlencode(params_w_offset)}",
        max_len=max_len,
        key=key,
        values=values,
    )

    urls: LStr = []

    for start, end in slices:
        params_l: LParam = params_common + [(key, s) for s in values[start:end]]
        query_s = urlencode(params_l, doseq=True)
        url_ = f"{url_base}?{query_s}"
        urls.append(url_)

    return urls


def _validate_values(values: Any) -> LValue:
    """Convert a value to a list and remove duplicates.

    :param values: The value to be converted.

    :return: A list of values.
    """
    if isinstance(values, TValues):
        return [values]
    values_ = _validate_value(values)
    return values_


def _validate_value(value: Any) -> LValue:
    """Check typing, remove duplicate values from list.

    :param value: The value to be validated.

    :return: A valid value.
    """
    if isinstance(value, TValues):
        return [value]
    if not isinstance(value, TLists):
        raise TypeError(f"{value=}, {TValues} expected")

    values: LValue = []
    for value_ in value:
        if not isinstance(value_, TValues):
            raise TypeError(f"{value_=}, {TValues} expected")
        values.append(value_)

    values = vlist.no_dupl(values)
    return values


def get_key_of_longest_value(params_d: DList) -> str:
    """Get the key of the parameter with the longest joined value.

    :param params_d: A dictionary of parameters.

    :return: The key of the parameter with the longest value.
    """
    if not params_d:
        return ""
    lengths_d = {}
    for key, values in params_d.items():
        value = "".join([str(i) for i in values])
        lengths_d[key] = len(value)
    max_key = max(lengths_d, key=lambda k: lengths_d[k])
    return max_key


def generate_offsets(count: int, limit: int, params_d: DAny, /) -> LDAny:
    """Generate a list of dictionaries with offset parameters.

    :param count: The total count of items to be processed.
    :param limit: The maximum limit for each batch.
    :param params_d: A dictionary containing other parameters.

    :return: A list of dictionaries with offset and other parameters.
    """
    if count <= 0 or limit <= 0:
        raise ValueError(f"{count=} {limit=}, value higher that 1 expected.")

    params: LDAny = []
    offset = 0
    while count > 0:
        limit_ = min(count, limit)
        params_d_ = params_d.copy()
        params_d_["limit"] = limit
        params_d_["offset"] = offset
        params.append(params_d_)
        offset += limit_
        count -= limit_

    return params
