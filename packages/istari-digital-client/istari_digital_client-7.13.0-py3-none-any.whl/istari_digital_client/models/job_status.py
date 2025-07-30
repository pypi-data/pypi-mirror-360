from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List
from istari_digital_client.models.job_status_name import JobStatusName
from typing import Optional, Set, TYPE_CHECKING
from typing_extensions import Self

from istari_digital_client.models.client_having import ClientHaving

if TYPE_CHECKING:
    from istari_digital_client.models.job import Job


class JobStatus(BaseModel, ClientHaving):
    """
    JobStatus
    """ # noqa: E501
    id: StrictStr
    created: datetime
    job_id: StrictStr
    name: JobStatusName
    created_by_id: Optional[StrictStr] = None
    message: Optional[StrictStr] = None
    agent_identifier: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["id", "created", "job_id", "name", "created_by_id", "message", "agent_identifier"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @property
    def job(self) -> Optional["Job"]:
        if not self.client:
            raise ValueError("Client is not set")
        return self.client.get_job(self.job_id)

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of JobStatus from a JSON string"""
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
        # set to None if created_by_id (nullable) is None
        # and model_fields_set contains the field
        if self.created_by_id is None and "created_by_id" in self.model_fields_set:
            _dict['created_by_id'] = None

        # set to None if message (nullable) is None
        # and model_fields_set contains the field
        if self.message is None and "message" in self.model_fields_set:
            _dict['message'] = None

        # set to None if agent_identifier (nullable) is None
        # and model_fields_set contains the field
        if self.agent_identifier is None and "agent_identifier" in self.model_fields_set:
            _dict['agent_identifier'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of JobStatus from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "job_id": obj.get("job_id"),
            "name": obj.get("name"),
            "created_by_id": obj.get("created_by_id"),
            "message": obj.get("message"),
            "agent_identifier": obj.get("agent_identifier")
        })
        return _obj
