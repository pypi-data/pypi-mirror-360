
from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Set
from typing_extensions import Self

from istari_digital_client.models.token import Token
from istari_digital_client.models.readable import Readable
from istari_digital_client.models.client_having import ClientHaving

class SnapshotRevisionSearchItem(BaseModel, ClientHaving, Readable):
    """
    SnapshotRevisionSearchItem
    """ # noqa: E501
    file_id: Optional[StrictStr]
    content_token: Token
    properties_token: Token
    name: Optional[StrictStr] = None
    extension: Optional[StrictStr] = None
    size: Optional[StrictInt] = None
    description: Optional[StrictStr] = None
    mime: Optional[StrictStr] = None
    version_name: Optional[StrictStr] = None
    external_identifier: Optional[StrictStr] = None
    display_name: Optional[StrictStr] = None
    schema_version: Optional[StrictStr] = None
    created_by_id: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["file_id", "content_token", "properties_token", "name", "extension", "size", "description", "mime", "version_name", "external_identifier", "display_name", "schema_version", "created_by_id"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def read_bytes(self) -> bytes:
        if self.client is None:
            raise ValueError("Client is not set")

        return self.client.read_contents(self.content_token)


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of SnapshotRevisionSearchItem from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of content_token
        if self.content_token:
            _dict['content_token'] = self.content_token.to_dict()
        # override the default output from pydantic by calling `to_dict()` of properties_token
        if self.properties_token:
            _dict['properties_token'] = self.properties_token.to_dict()
        # set to None if file_id (nullable) is None
        # and model_fields_set contains the field
        if self.file_id is None and "file_id" in self.model_fields_set:
            _dict['file_id'] = None

        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if extension (nullable) is None
        # and model_fields_set contains the field
        if self.extension is None and "extension" in self.model_fields_set:
            _dict['extension'] = None

        # set to None if size (nullable) is None
        # and model_fields_set contains the field
        if self.size is None and "size" in self.model_fields_set:
            _dict['size'] = None

        # set to None if description (nullable) is None
        # and model_fields_set contains the field
        if self.description is None and "description" in self.model_fields_set:
            _dict['description'] = None

        # set to None if mime (nullable) is None
        # and model_fields_set contains the field
        if self.mime is None and "mime" in self.model_fields_set:
            _dict['mime'] = None

        # set to None if version_name (nullable) is None
        # and model_fields_set contains the field
        if self.version_name is None and "version_name" in self.model_fields_set:
            _dict['version_name'] = None

        # set to None if external_identifier (nullable) is None
        # and model_fields_set contains the field
        if self.external_identifier is None and "external_identifier" in self.model_fields_set:
            _dict['external_identifier'] = None

        # set to None if display_name (nullable) is None
        # and model_fields_set contains the field
        if self.display_name is None and "display_name" in self.model_fields_set:
            _dict['display_name'] = None

        # set to None if schema_version (nullable) is None
        # and model_fields_set contains the field
        if self.schema_version is None and "schema_version" in self.model_fields_set:
            _dict['schema_version'] = None

        # set to None if created_by_id (nullable) is None
        # and model_fields_set contains the field
        if self.created_by_id is None and "created_by_id" in self.model_fields_set:
            _dict['created_by_id'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SnapshotRevisionSearchItem from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "file_id": obj.get("file_id"),
            "content_token": Token.from_dict(obj["content_token"]) if obj.get("content_token") is not None else None,
            "properties_token": Token.from_dict(obj["properties_token"]) if obj.get("properties_token") is not None else None,
            "name": obj.get("name"),
            "extension": obj.get("extension"),
            "size": obj.get("size"),
            "description": obj.get("description"),
            "mime": obj.get("mime"),
            "version_name": obj.get("version_name"),
            "external_identifier": obj.get("external_identifier"),
            "display_name": obj.get("display_name"),
            "schema_version": obj.get("schema_version"),
            "created_by_id": obj.get("created_by_id")
        })
        return _obj
