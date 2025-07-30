from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Set, TYPE_CHECKING
from typing_extensions import Self

from istari_digital_client.models.comment import Comment
from istari_digital_client.models.file import File
from istari_digital_client.models.function_auth_type import FunctionAuthType
from istari_digital_client.models.resource_archive_status import ResourceArchiveStatus
from istari_digital_client.models.file_having import FileHaving
from istari_digital_client.models.client_having import ClientHaving


class FunctionAuthSecret(ClientHaving, FileHaving):
    """
    A class representing a FunctionAuthSecret.
    """ # noqa: E501
    id: StrictStr
    created: datetime
    file: File
    comments: List[Comment]
    archive_status_history: List[ResourceArchiveStatus]
    created_by_id: StrictStr
    function_auth_provider_id: StrictStr
    function_auth_type: FunctionAuthType
    sha: StrictStr
    salt: StrictStr
    expiration: Optional[datetime] = None
    __client_fields__: ClassVar[List[str]] = ["file", "comments"]
    __properties: ClassVar[List[str]] = ["id", "created", "file", "comments", "archive_status_history", "created_by_id", "function_auth_provider_id", "function_auth_type", "sha", "salt", "expiration"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
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
        """Create an instance of FunctionAuthSecret from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of file
        if self.file:
            _dict['file'] = self.file.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in comments (list)
        _items = []
        if self.comments:
            for _item_comments in self.comments:
                if _item_comments:
                    _items.append(_item_comments.to_dict())
            _dict['comments'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in archive_status_history (list)
        _items = []
        if self.archive_status_history:
            for _item_archive_status_history in self.archive_status_history:
                if _item_archive_status_history:
                    _items.append(_item_archive_status_history.to_dict())
            _dict['archive_status_history'] = _items
        # set to None if expiration (nullable) is None
        # and model_fields_set contains the field
        if self.expiration is None and "expiration" in self.model_fields_set:
            _dict['expiration'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FunctionAuthSecret from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "file": File.from_dict(obj["file"]) if obj.get("file") is not None else None,
            "comments": [Comment.from_dict(_item) for _item in obj["comments"]] if obj.get("comments") is not None else None,
            "archive_status_history": [ResourceArchiveStatus.from_dict(_item) for _item in obj["archive_status_history"]] if obj.get("archive_status_history") is not None else None,
            "created_by_id": obj.get("created_by_id"),
            "function_auth_provider_id": obj.get("function_auth_provider_id"),
            "function_auth_type": obj.get("function_auth_type"),
            "sha": obj.get("sha"),
            "salt": obj.get("salt"),
            "expiration": obj.get("expiration")
        })
        return _obj
