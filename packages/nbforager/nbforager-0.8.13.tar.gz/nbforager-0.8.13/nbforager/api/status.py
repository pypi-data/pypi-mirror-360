"""Status connectors."""

from nbforager.api.connector import Connector
from nbforager.types_ import DAny


class StatusC(Connector):
    """StatusC."""

    path = "status/"

    def get(self, **kwargs) -> DAny:  # type: ignore
        """Get status.

        :return: Dictionary with status data.
        """
        _ = kwargs  # noqa
        return self._get_d()
