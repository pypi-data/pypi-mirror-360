import abc
from typing import TYPE_CHECKING, Optional, ClassVar, List

if TYPE_CHECKING:
    from istari_digital_client.api.client_api import ClientApi


class ClientHaving(abc.ABC):
    _client: Optional["ClientApi"] = None
    __client_fields__: ClassVar[List[str]] = []

    @property
    def client(self) -> Optional["ClientApi"]:
        return self._client

    @client.setter
    def client(self, value: "ClientApi"):
        self._client = value

        for name in self.__client_fields__:
            attr = getattr(self, name, None)

            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, 'client'):
                        item.client = value
            elif attr is not None and hasattr(attr, 'client'):
                attr.client = value
