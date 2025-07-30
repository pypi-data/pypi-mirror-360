from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set, TYPE_CHECKING
from typing_extensions import Self

from istari_digital_client.models.client_having import ClientHaving

if TYPE_CHECKING:
    from istari_digital_client.models.file import File
    from istari_digital_client.api.client_api import Resource
    from istari_digital_client.models.file_revision import FileRevision


class Product(BaseModel, ClientHaving):
    """
    Product
    """ # noqa: E501
    revision_id: StrictStr
    file_id: Optional[StrictStr] = None
    resource_type: Optional[StrictStr] = None
    resource_id: Optional[StrictStr] = None
    relationship_identifier: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["revision_id", "file_id", "resource_type", "resource_id", "relationship_identifier"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @property
    def file(self) -> Optional["File"]:
        if self.file_id is None or self.client is None:
            return None
        return self.client.get_file(self.file_id)

    @property
    def resource(self) -> Optional["Resource"]:
        file = self.file
        if self.resource_type is None or self.resource_id is None or self.client is None:
            return None
        return self.client.get_resource(self.resource_type, self.resource_id)

    @property
    def revision(self) -> Optional["FileRevision"]:
        if self.revision_id is None or self.client is None:
            return None
        return self.client.get_revision(self.revision_id)

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Product from a JSON string"""
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
        # set to None if file_id (nullable) is None
        # and model_fields_set contains the field
        if self.file_id is None and "file_id" in self.model_fields_set:
            _dict['file_id'] = None

        # set to None if resource_type (nullable) is None
        # and model_fields_set contains the field
        if self.resource_type is None and "resource_type" in self.model_fields_set:
            _dict['resource_type'] = None

        # set to None if resource_id (nullable) is None
        # and model_fields_set contains the field
        if self.resource_id is None and "resource_id" in self.model_fields_set:
            _dict['resource_id'] = None

        # set to None if relationship_identifier (nullable) is None
        # and model_fields_set contains the field
        if self.relationship_identifier is None and "relationship_identifier" in self.model_fields_set:
            _dict['relationship_identifier'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Product from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "revision_id": obj.get("revision_id"),
            "file_id": obj.get("file_id"),
            "resource_type": obj.get("resource_type"),
            "resource_id": obj.get("resource_id"),
            "relationship_identifier": obj.get("relationship_identifier")
        })
        return _obj
