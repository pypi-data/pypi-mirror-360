"""Exceptions."""


class NbApiError(Exception):
    """Invalid dict key in Netbox data."""


class NbParserError(Exception):
    """Parsing error in Netbox data."""
