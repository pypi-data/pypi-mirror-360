import abc

import inflection
from pydantic import StrictStr
from typing import TYPE_CHECKING, Optional, Callable

from istari_digital_client.models.archive import Archive
from istari_digital_client.models.restore import Restore

if TYPE_CHECKING:
    from istari_digital_client.api.client_api import ClientApi

class Archivable(abc.ABC):
    def _require_client(self) -> "ClientApi":
        """Internal helper to assert that a client exists."""
        client = getattr(self, "client", None)
        if client is None:
            raise ValueError(f"`client` is not set for instance of {self.__class__.__name__}")
        return client

    @property
    def _id(self) -> StrictStr:
        """The ID of the item to be archived or restored."""
        item_id = getattr(self, "id", None)

        if item_id is None:
            raise ValueError("id is not set")

        return item_id

    def archive(self, archive_reason: Optional[str] = None):
        """
        Archive the item using the appropriate client method based on its type.

        Args:
            archive_reason (Optional[str]): Reason for archiving.

        Raises:
            ValueError: If `client` is not set or class type is not archivable.
        """
        client = self._require_client()
        reason = Archive(reason=archive_reason) if archive_reason else None
        method_name = f"archive_{inflection.underscore(self.__class__.__name__)}"
        method: Callable[[StrictStr, Optional[Archive]], object] = getattr(client, method_name)

        try:
            return method(self._id, reason)
        except ValueError:
            raise ValueError(f"Cannot archive {self.__class__.__name__} with id {self._id}. Ensure the client is set and the item is archivable.")

    def restore(self, restore_reason: Optional[str] = None):
        """
        Restore the item using the appropriate client method based on its type.

        Args:
            restore_reason (Optional[str]): Reason for restoring.

        Raises:
            ValueError: If `client` is not set or class type is not restorable.
        """
        client = self._require_client()
        reason = Restore(reason=restore_reason) if restore_reason else None
        method_name = f"restore_{inflection.underscore(self.__class__.__name__)}"
        method: Callable[[StrictStr, Optional[Restore]], object] = getattr(client, method_name)

        try:
            return method(self._id, reason)
        except ValueError:
            raise ValueError(f"Cannot restore {self.__class__.__name__} with id {self._id}. Ensure the client is set and the item is restorable.")
