# pylint: disable=R0904

"""NbParser."""

from functools import wraps
from typing import Any, Type, Dict, List

from vhelpers import vstr, vlist

from nbforager.exceptions import NbParserError
from nbforager.types_ import DAny, Int, Str, LDAny, TLists, SeqUIntStr


def check_strict(method):
    """Wrap method to check value.

    :param method: The method to be decorated.

    :return: The decorated function.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrap."""
        result = method(self, *args, **kwargs)
        if self.strict and not result:
            keys = "/".join(args)
            raise NbParserError(f"{keys=} expected in {self._source()}.")
        return result

    return wrapper


def check_in_strict_manner(method):
    """Wrap method to check value in strict manner, returned value is mandatory.

    :param method: The method to be decorated.

    :return: The decorated function.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrap."""
        strict_actual = self.strict
        self.strict = True

        result = method(self, *args, **kwargs)

        self.strict = strict_actual
        if not result:
            keys = "/".join(args)
            raise NbParserError(f"{keys=} expected in {self._source()}.")

        return result

    return wrapper


class NbParser:
    """Dictionary parser for extracting values from a Netbox object using a chain of keys.

    Netbox object may have None instead of a dictionary when a related object is absent,
    requiring constant data type checks. NbParser ensures the desired value is returned
    with the correct data type, even if the data is missing.

    Raises NbParserError if strict=True and some keys are missing.
    """

    def __init__(self, data: DAny, strict: bool = False, **kwargs):  # pylint: disable=E0601
        """Init NbParser.

        :param data: Netbox object.
        :type data: dict

        :param strict: True - if data is invalid raise NbParserError,
            False - if data is invalid return empty data with proper type.
        :type strict: bool

        :param version: Netbox version.
            Designed for compatibility with different versions.
        :type version: str
        """
        self.data = _init_data(data)
        self.strict = strict
        self.version = str(kwargs.get("version") or "0")

    def __repr__(self):
        """__repr__."""
        data = None
        if isinstance(self.data, dict):
            for key in ["name", "prefix", "address", "cid", "object_type", "id"]:
                if value := self.data.get(key):
                    data = vstr.repr_params(**{key: str(value)})
                    break

        name = self.__class__.__name__
        return f"<{name}: {data}>"

    # ====================== universal get methods =======================

    def any(self, *keys) -> Any:
        """Get any value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Value or None if the value is absent.
        :rtype: Any
        """
        try:
            return self._get_keys(type_=type(None), keys=keys, data=self.data)
        except NbParserError:
            return None

    def bool(self, *keys) -> bool:
        """Get bool value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Boolean value or False if the value is absent.
        :rtype: bool
        """
        return self._get_keys(type_=bool, keys=keys, data=self.data)

    def dict(self, *keys) -> Dict:
        """Get dictionary value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Dictionary value or an empty dictionary if the value is absent.
        :rtype: dict

        :raise NbParserError: If strict=True and the value is not a dictionary or key is absent.
        """
        return self._get_keys(type_=dict, keys=keys, data=self.data)

    def int(self, *keys) -> int:
        """Get integer value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Integer value or 0 if the value is absent.
        :rtype: int

        :raise NbParserError: If strict=True and the value is not a digit or key is absent.
        """
        data = self.data
        try:
            for key in keys:
                data = data[key]
        except (KeyError, TypeError) as ex:
            if self.strict:
                type_ = type(ex).__name__
                raise NbParserError(f"{type_}: {ex}, {keys=} in {self._source()}") from ex
            return 0

        if isinstance(data, int):
            return data

        if isinstance(data, str) and data.isdigit():
            return int(data)

        if self.strict:
            raise NbParserError(f"{keys=} {int} expected in {self._source()}.")
        return 0

    def list(self, *keys) -> List:
        """Get list value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: List value or an empty list if the value is absent.
        :rtype: list

        :raise NbParserError: If strict=True and the value is not a list or key is absent.
        """
        return self._get_keys(type_=list, keys=keys, data=self.data)

    def str(self, *keys) -> str:
        """Get string value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: String value or an empty string if the value is absent.
        :rtype: str

        :raise NbParserError: If strict=True and the value is not a string or key is absent.
        """
        return self._get_keys(type_=str, keys=keys, data=self.data)

    # ======================== strict get methods ========================

    @check_in_strict_manner
    def strict_dict(self, *keys) -> Dict:
        """Get dictionary value by keys in strict manner, value is mandatory.

        Useful when strict=False, but you need to obtain a value in a strict manner.
        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Dictionary value.
        :rtype: dict

        :raise NbParserError: If the value is not a dictionary or key is absent or value is empty.
        """
        return self.dict(*keys)

    @check_in_strict_manner
    def strict_int(self, *keys) -> Int:
        """Get integer value by keys in strict manner, value is mandatory.

        Useful when strict=False, but you need to obtain a value in a strict manner.
        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Integer value.
        :rtype: int

        :raise NbParserError: If the value is not int or key is absent or value is 0.
        """
        return self.int(*keys)

    @check_in_strict_manner
    def strict_list(self, *keys) -> List:
        """Get string value by keys in strict manner, value is mandatory.

        Useful when strict=False, but you need to obtain a value in a strict manner.
        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: List value.
        :rtype: list

        :raise NbParserError: If the value is not a list or key is absent or value is empty.
        """
        return self.list(*keys)

    @check_in_strict_manner
    def strict_str(self, *keys) -> Str:
        """Get string value by keys in strict manner, value is mandatory.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: String value.
        :rtype: str

        :raise NbParserError: If the value is not a string or key is absent or value is absent.
        """
        return self.str(*keys)

    # ============================= helpers ==============================

    def _get_keys(self, type_: Type, keys: SeqUIntStr, data: Dict) -> Any:
        """Retrieve values from data using keys and check their data types.

        :param type_: Data type.
        :param keys: Chaining dictionary keys to retrieve the desired value.
        :param data: Dictionary.

        :return: Value with proper data type.

        :raise NbParserError: If strict=True and key absent or type not match.
        """
        try:
            for key in keys:
                data = data[key]  # type: ignore
        except (KeyError, IndexError, TypeError) as ex:
            if self.strict:
                ex_type = type(ex).__name__
                raise NbParserError(f"{ex_type}: {ex}, {keys=} in {self._source()}.") from ex
            return type_()

        if type_ is type(None):
            return data
        if not isinstance(data, type_):
            if self.strict:
                ex_type = "TypeError"
                raise NbParserError(f"{ex_type}: {keys=} {type_} expected in {self._source()}.")
            return type_()

        return data

    def _source(self) -> Str:
        """Return URL or dictionary of source object."""
        if isinstance(self.data, dict):
            if url := self.data.get("url"):
                return str(url)
        return str(self.data)


def _init_data(data: DAny) -> DAny:
    """Init data."""
    if data is None:
        return {}
    if isinstance(data, dict):
        return data
    raise TypeError(f"{data=} {dict} expected.")


# ============================ functions =============================


def find_objects(objects: LDAny, **kwargs) -> LDAny:
    """Find Netbox objects in tree by extended finding parameters.

    :param objects: Netbox objects where searching is required using kwargs.
    :param kwargs: Extended filtering parameters.
    :return: Filtered Netbox objects.
    """
    if not kwargs:
        return objects
    (key, values), *key_values = list(kwargs.items())
    if not isinstance(values, TLists):
        values = [values]

    objects_: LDAny = []
    for data in objects:
        keys = key.split("__")
        if len(keys) <= 1:
            keys = [key]
        if keys[0] == "tags":
            if len(keys) != 2:
                raise ValueError(f"{keys=} {len(keys)=} expected 2.")
            values_ = [d[keys[1]] for d in data["tags"]]
            if vlist.is_in(values_, values):
                objects_.append(data)
        else:
            value_ = NbParser(data).any(*keys)
            if value_ in values:
                objects_.append(data)

    if key_values:
        objects_ = find_objects(objects=objects_, **dict(key_values))
    return objects_
