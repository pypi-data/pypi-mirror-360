from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List
from istari_digital_client.models.file import File
from typing import Optional, Set, TYPE_CHECKING
from typing_extensions import Self

from istari_digital_client.models.file_having import FileHaving
from istari_digital_client.models.client_having import ClientHaving

if TYPE_CHECKING:
    from istari_digital_client.models.model import Model
    from istari_digital_client.models.page_artifact import PageArtifact
    from istari_digital_client.models.page_comment import PageComment
    from istari_digital_client.models.page_job import PageJob


class ModelListItem(ClientHaving, FileHaving):
    """
    Model class with unresolved sub-class replaced with lists of uuids.
    """ # noqa: E501
    id: StrictStr
    created: datetime
    file: File
    archive_status: StrictStr
    created_by_id: StrictStr
    comment_ids: Optional[List[StrictStr]] = None
    artifact_ids: Optional[List[StrictStr]] = None
    job_ids: Optional[List[StrictStr]] = None
    __client_fields__: ClassVar[List[str]] = ["file"]
    __properties: ClassVar[List[str]] = ["id", "created", "file", "archive_status", "created_by_id", "comment_ids", "artifact_ids", "job_ids"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @property
    def model(self) -> Optional["Model"]:
        if not self.client:
            return None
        return self.client.get_model(self.id)

    @property
    def comments(self) -> Optional[PageComment]:
        if not self.comment_ids or not self.client:
            return None
        return self.client.list_model_comments(self.id)

    @property
    def artifacts(self) -> Optional[PageArtifact]:
        if not self.artifact_ids or not self.client:
            return None
        return self.client.list_model_artifacts(self.id)

    @property
    def jobs(self) -> Optional[PageJob]:
        if not self.job_ids or not self.client:
            return None
        return self.client.list_model_jobs(self.id)

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of ModelListItem from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ModelListItem from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "file": File.from_dict(obj["file"]) if obj.get("file") is not None else None,
            "archive_status": obj.get("archive_status"),
            "created_by_id": obj.get("created_by_id"),
            "comment_ids": obj.get("comment_ids"),
            "artifact_ids": obj.get("artifact_ids"),
            "job_ids": obj.get("job_ids")
        })
        return _obj
