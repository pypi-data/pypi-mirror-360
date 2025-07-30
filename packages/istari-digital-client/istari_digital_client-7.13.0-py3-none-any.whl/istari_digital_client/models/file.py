from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Set, TYPE_CHECKING
from typing_extensions import Self

from istari_digital_client.models.control_tag import ControlTag
from istari_digital_client.models.file_archive_status import FileArchiveStatus
from istari_digital_client.models.file_revision import FileRevision
from istari_digital_client.models.file_revision_having import FileRevisionHaving
from istari_digital_client.models.shareable import Shareable
from istari_digital_client.models.archivable import Archivable
from istari_digital_client.models.client_having import ClientHaving

if TYPE_CHECKING:
    from istari_digital_client.api.client_api import Resource


class File(ClientHaving, FileRevisionHaving, Shareable, Archivable):
    """
    A class representing a file.
    """  # noqa: E501

    id: StrictStr
    created: datetime
    revisions: List[FileRevision]
    archive_status_history: List[FileArchiveStatus]
    resource_id: Optional[StrictStr] = None
    resource_type: Optional[StrictStr] = None
    created_by_id: Optional[StrictStr] = None
    control_tags: Optional[List[ControlTag]] = None
    __client_fields__: ClassVar[List[str]] = ["revisions"]
    __properties: ClassVar[List[str]] = [
        "id",
        "created",
        "revisions",
        "archive_status_history",
        "resource_id",
        "resource_type",
        "created_by_id",
    ]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True,
    )

    @property
    def revision(self) -> FileRevision:
        return self.revisions[-1]

    @property
    def resource(self) -> "Resource":
        if self.client is None:
            raise ValueError("client is not set")
        if self.resource_id is None:
            raise ValueError("resource_id is not set")
        if self.resource_type is None:
            raise ValueError("resource_type is not set")
        return self.client.get_resource(self.resource_type, self.resource_id)

    @property
    def archive_status(self) -> FileArchiveStatus:
        return self.archive_status_history[-1]

    def update_properties(
        self,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        external_identifier: Optional[str] = None,
        version_name: Optional[str] = None,
    ) -> "File":
        if self.client is None:
            raise ValueError("client is not set")

        return self.client.update_revision_properties(
            self.revision,
            description=description,
            display_name=display_name,
            external_identifier=external_identifier,
            version_name=version_name,
        )

    def update_description(self, description: str) -> "File":
        return self.update_properties(
            description=description,
        )

    def update_display_name(self, display_name: str) -> "File":
        return self.update_properties(
            display_name=display_name,
        )

    def update_external_identifier(self, external_identifier: str) -> "File":
        return self.update_properties(
            external_identifier=external_identifier,
        )

    def update_version_name(self, version_name: str) -> "File":
        return self.update_properties(
            version_name=version_name,
        )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of File from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in revisions (list)
        _items = []
        if self.revisions:
            for _item_revisions in self.revisions:
                if _item_revisions:
                    _items.append(_item_revisions.to_dict())
            _dict["revisions"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in archive_status_history (list)
        _items = []
        if self.archive_status_history:
            for _item_archive_status_history in self.archive_status_history:
                if _item_archive_status_history:
                    _items.append(_item_archive_status_history.to_dict())
            _dict["archive_status_history"] = _items
        # set to None if resource_id (nullable) is None
        # and model_fields_set contains the field
        if self.resource_id is None and "resource_id" in self.model_fields_set:
            _dict["resource_id"] = None

        # set to None if resource_type (nullable) is None
        # and model_fields_set contains the field
        if self.resource_type is None and "resource_type" in self.model_fields_set:
            _dict["resource_type"] = None

        # set to None if created_by_id (nullable) is None
        # and model_fields_set contains the field
        if self.created_by_id is None and "created_by_id" in self.model_fields_set:
            _dict["created_by_id"] = None

        # override the default output from pydantic by calling `to_dict()` of each item in control_tags (list)
        _items = []
        if self.control_tags:
            for _item_control_tags in self.control_tags:
                if _item_control_tags:
                    _items.append(_item_control_tags.to_dict())
            _dict['control_tags'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of File from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "id": obj.get("id"),
                "created": obj.get("created"),
                "revisions": [
                    FileRevision.from_dict(_item) for _item in obj["revisions"]
                ]
                if obj.get("revisions") is not None
                else None,
                "archive_status_history": [
                    FileArchiveStatus.from_dict(_item)
                    for _item in obj["archive_status_history"]
                ]
                if obj.get("archive_status_history") is not None
                else None,
                "resource_id": obj.get("resource_id"),
                "resource_type": obj.get("resource_type"),
                "created_by_id": obj.get("created_by_id"),
                "control_tags": [ControlTag.from_dict(_item) for _item in obj["control_tags"]] if obj.get("control_tags") is not None else None
            }
        )
        return _obj
