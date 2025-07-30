from __future__ import annotations
import pprint
import re  # noqa: F401
import json
import uuid
import hashlib
import logging
import traceback
import tempfile
from threading import Lock
from pathlib import Path

from datetime import datetime, timezone
from functools import cached_property

from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr, PrivateAttr
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING, ClassVar
from typing_extensions import Self

from istari_digital_client.models.file_revision_archive_status import (
    FileRevisionArchiveStatus,
)
from istari_digital_client.models.archive_status_name import ArchiveStatusName
from istari_digital_client.models.product import Product
from istari_digital_client.models.source import Source
from istari_digital_client.models.token import Token
from istari_digital_client.models.properties import Properties

from istari_digital_client.models.readable import Readable
from istari_digital_client.models.archivable import Archivable
from istari_digital_client.models.client_having import ClientHaving

import istari_digital_core

if TYPE_CHECKING:
    from istari_digital_client.models.file import File
    from istari_digital_client.api.client_api import Resource

logger = logging.getLogger("istari-digital-client.token_reader")


class ReadError(IOError):
    pass


class CacheError(Exception):
    pass


class InvalidChecksumError(ValueError):
    pass


class FileRevision(BaseModel, ClientHaving, Readable, Archivable):
    """
    Represents a file revision object.  This class inherits from the Base classes.
    """  # noqa: E501

    id: StrictStr
    created: datetime
    file_id: Optional[StrictStr]
    content_token: Token
    properties_token: Token
    archive_status_history: List[FileRevisionArchiveStatus]
    name: Optional[StrictStr] = None
    stem: Optional[StrictStr] = None
    suffix: Optional[StrictStr] = None
    extension: Optional[StrictStr] = None
    description: Optional[StrictStr] = None
    size: Optional[StrictInt] = None
    mime: Optional[StrictStr] = None
    version_name: Optional[StrictStr] = None
    external_identifier: Optional[StrictStr] = None
    display_name: Optional[StrictStr] = None
    sources: Optional[List[Source]] = None
    products: Optional[List[Product]] = None
    created_by_id: Optional[StrictStr] = None

    # Private attributes
    _cache_path_lock_timeout: int = PrivateAttr(default=2)
    _filesystem_cache_hits: int = PrivateAttr(default=0)
    _filesystem_cache_misses: int = PrivateAttr(default=0)
    _filesystem_cache_puts: int = PrivateAttr(default=0)

    __client_fields__: ClassVar[List[str]] = ["sources", "products"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True,
    )

    def __post_init__(self):
        self.stem = Path(self.name).stem if self.name else None
        self.suffix = Path(self.name).suffix if self.name else None

    @property
    def file(self) -> Optional["File"]:
        if self.file_id is None:
            raise ReadError("File ID is not set")
        if self.client is None:
            raise ReadError("Client is not set")
        return self.client.get_file(self.file_id)

    @property
    def resource(self) -> Optional["Resource"]:
        file = self.file
        if file is None or self.client is None or file.resource_type is None or file.resource_id is None:
            return None

        return self.client.get_resource(file.resource_type, file.resource_id)

    def source_revision_ids(self) -> Optional[list[str]]:
        if not self.sources:
            return None
        return [source.revision_id for source in self.sources]

    def source_product_ids(self) -> Optional[list[str]]:
        if not self.products:
            return None
        return [product.revision_id for product in self.products]

    @property
    def archive_status(self) -> FileRevisionArchiveStatus:
        return self.archive_status_history[-1]

    @property
    def properties(self) -> Properties:
        if self.client is None:
            raise ReadError("Client is not set")
        return self.client.read_properties(self.properties_token)

    def read_bytes(self) -> bytes:
        if self.client is None:
            raise ReadError("Client is not set")
        if self.client.config.filesystem_cache_enabled:
            return self._filesystem_caching_read_bytes()
        return self.client.read_contents(self.content_token)

    def __del__(self):
        """Delete cached content."""
        if self._cache_path is not None:
            self._cache_path.unlink(missing_ok=True)

    @cached_property
    def _cache_path_lock(self) -> Lock:
        return Lock()

    @cached_property
    def _log_msg_pfx(self) -> str:
        return f"token {self.id} -"

    def _cache_identifier(self, size: int = 16) -> str:
        _hash = hashlib.shake_256()
        _hash.update(self.content_token.sha.encode("utf-8"))
        _hash.update(self.content_token.salt.encode("utf-8"))
        return _hash.hexdigest(size)

    @cached_property
    def _cache_dir(self) -> Path:
        if self.client is None:
            raise CacheError("Client is not set")
        subdir = self._cache_identifier(2)
        _dir = self.client.config.filesystem_cache_root / subdir
        _dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        return _dir

    @cached_property
    def _cache_name(self) -> str:
        return self._cache_identifier(32)

    @cached_property
    def _cache_path(self) -> Optional[Path]:
        if self.client is None:
            return None
        return self._cache_dir / self._cache_name

    def _cache_dir_mktemp(self) -> Path:
        return Path(
            tempfile.mktemp(
                suffix=str(uuid.uuid4()) + ".tmp",
                prefix=self._cache_name,
                dir=self._cache_dir,
            )
        )

    def _checksum_verified(self, data: bytes) -> bytes:
        if self._cache_path is None:
            raise CacheError("Cache path is not set")
        data = self._cache_path.read_bytes()
        _hash = hashlib.sha384()
        _hash.update(data)
        _hash.update(self.content_token.salt.encode("utf-8"))
        actual = _hash.hexdigest()
        expected = self.content_token.sha
        if not actual == expected:
            msg = f"Token data content checksum is invalid ({actual} != {expected})"
            raise InvalidChecksumError(msg)
        return data

    def _checksum_verified_cache_read(self) -> bytes:
        if self._cache_path is None:
            raise CacheError("Cache path is not set")
        if not self._cache_path.exists():
            raise FileNotFoundError(self._cache_path)
        data = self._checksum_verified(self._cache_path.read_bytes())
        return data

    def _filesystem_caching_read_bytes(self) -> bytes:
        if self.client is None:
            raise ReadError("Client is not set")
        if self._cache_path is None:
            raise CacheError("Cache path is not set")
        with self._cache_path_lock:
            try:
                data = self._checksum_verified_cache_read()
                self._filesystem_cache_hits += 1
                return data
            except Exception:
                self._filesystem_cache_misses += 1
                logger.debug("%s", traceback.format_exc())
                if not self._cache_dir.exists():
                    self._cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                if self._cache_path.exists():
                    self._cache_path.unlink(missing_ok=True)
                temp_path = Path(self._cache_dir_mktemp())
                logger.debug("%s downloading to %s", self._log_msg_pfx, temp_path)
                data = self.client.read_contents(self.content_token)
                temp_path.write_bytes(data)
                size = temp_path.stat().st_size
                temp_path.replace(self._cache_path)
                logger.debug(
                    "%s downloaded contents to filesystem cache (size: %d): %s",
                    self._log_msg_pfx,
                    size,
                    self._cache_path,
                )
                self._filesystem_cache_puts += 1
                return self._checksum_verified(data)

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of FileRevision from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of content_token
        if self.content_token:
            _dict["content_token"] = self.content_token.to_dict()
        # override the default output from pydantic by calling `to_dict()` of properties_token
        if self.properties_token:
            _dict["properties_token"] = self.properties_token.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in archive_status_history (list)
        _items = []
        if self.archive_status_history:
            for _item_archive_status_history in self.archive_status_history:
                if _item_archive_status_history:
                    _items.append(_item_archive_status_history.to_dict())
            _dict["archive_status_history"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in sources (list)
        _items = []
        if self.sources:
            for _item_sources in self.sources:
                if _item_sources:
                    _items.append(_item_sources.to_dict())
            _dict["sources"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in products (list)
        _items = []
        if self.products:
            for _item_products in self.products:
                if _item_products:
                    _items.append(_item_products.to_dict())
            _dict["products"] = _items
        # set to None if file_id (nullable) is None
        # and model_fields_set contains the field
        if self.file_id is None and "file_id" in self.model_fields_set:
            _dict["file_id"] = None

        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict["name"] = None

        # set to None if extension (nullable) is None
        # and model_fields_set contains the field
        if self.extension is None and "extension" in self.model_fields_set:
            _dict["extension"] = None

        # set to None if size (nullable) is None
        # and model_fields_set contains the field
        if self.size is None and "size" in self.model_fields_set:
            _dict["size"] = None

        # set to None if description (nullable) is None
        # and model_fields_set contains the field
        if self.description is None and "description" in self.model_fields_set:
            _dict["description"] = None

        # set to None if mime (nullable) is None
        # and model_fields_set contains the field
        if self.mime is None and "mime" in self.model_fields_set:
            _dict["mime"] = None

        # set to None if version_name (nullable) is None
        # and model_fields_set contains the field
        if self.version_name is None and "version_name" in self.model_fields_set:
            _dict["version_name"] = None

        # set to None if external_identifier (nullable) is None
        # and model_fields_set contains the field
        if (
            self.external_identifier is None
            and "external_identifier" in self.model_fields_set
        ):
            _dict["external_identifier"] = None

        # set to None if display_name (nullable) is None
        # and model_fields_set contains the field
        if self.display_name is None and "display_name" in self.model_fields_set:
            _dict["display_name"] = None

        # set to None if created_by_id (nullable) is None
        # and model_fields_set contains the field
        if self.created_by_id is None and "created_by_id" in self.model_fields_set:
            _dict["created_by_id"] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FileRevision from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "id": obj.get("id"),
                "created": obj.get("created"),
                "file_id": obj.get("file_id"),
                "content_token": Token.from_dict(obj["content_token"])
                if obj.get("content_token") is not None
                else None,
                "properties_token": Token.from_dict(obj["properties_token"])
                if obj.get("properties_token") is not None
                else None,
                "archive_status_history": [
                    FileRevisionArchiveStatus.from_dict(_item)
                    for _item in obj["archive_status_history"]
                ]
                if obj.get("archive_status_history") is not None
                else None,
                "name": obj.get("name"),
                "extension": obj.get("extension"),
                "size": obj.get("size"),
                "description": obj.get("description"),
                "mime": obj.get("mime"),
                "version_name": obj.get("version_name"),
                "external_identifier": obj.get("external_identifier"),
                "display_name": obj.get("display_name"),
                "sources": [Source.from_dict(_item) for _item in obj["sources"]]
                if obj.get("sources") is not None
                else None,
                "products": [Product.from_dict(_item) for _item in obj["products"]]
                if obj.get("products") is not None
                else None,
                "created_by_id": obj.get("created_by_id"),
            }
        )
        _obj.stem = Path(_obj.name).stem if _obj.name else None
        _obj.suffix = Path(_obj.name).suffix if _obj.name else None

        return _obj

    @classmethod
    def from_storage_revision(
        cls,
        storage_revision: istari_digital_core.Revision,
        sources: Optional[List[Source]],
    ) -> Self:
        file_revision_id = str(uuid.uuid4())

        file_revision_archive_status = FileRevisionArchiveStatus(
            id=str(uuid.uuid4()),
            created=datetime.now(timezone.utc),
            name=ArchiveStatusName.ACTIVE,
            reason="Initial",
            created_by_id=None,
            file_revision_id=file_revision_id,
        )

        return cls(
            id=file_revision_id,
            created=datetime.now(timezone.utc),
            file_id=None,
            content_token=Token.from_storage_token(storage_revision.content_token),
            properties_token=Token.from_storage_token(storage_revision.properties_token),
            archive_status_history=[file_revision_archive_status],
            name=storage_revision.properties.file_name,
            extension=storage_revision.properties.extension,
            size=storage_revision.properties.size,
            description=storage_revision.properties.description,
            mime=storage_revision.properties.mime,
            version_name=storage_revision.properties.version_name,
            external_identifier=storage_revision.properties.external_identifier,
            display_name=storage_revision.properties.display_name,
            sources=sources,
            products=None,
            created_by_id=None,
        )
