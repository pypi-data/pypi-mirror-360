from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List
from istari_digital_client.models.agent_display_name import AgentDisplayName
from istari_digital_client.models.agent_information import AgentInformation
from istari_digital_client.models.agent_modules import AgentModules
from istari_digital_client.models.agent_status import AgentStatus
from typing import Optional, Set
from typing_extensions import Self


class Agent(BaseModel):
    """
    Agent
    """ # noqa: E501
    id: StrictStr
    created: datetime
    agent_identifier: StrictStr
    display_name_history: Optional[List[AgentDisplayName]] = None
    information_history: Optional[List[AgentInformation]] = None
    status_history: Optional[List[AgentStatus]] = None
    modules_history: Optional[List[AgentModules]] = None
    created_by_id: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["id", "created", "agent_identifier", "information_history", "status_history", "modules_history", "created_by_id"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @property
    def display_name(self) -> Optional[AgentDisplayName]:
        """Returns the latest display name record"""
        return self.display_name_history[-1] if self.display_name_history else None

    @property
    def information(self) -> Optional[AgentInformation]:
        """Returns the latest information record"""
        return self.information_history[-1] if self.information_history else None

    @property
    def agent_version(self) -> Optional[str]:
        """Returns the latest agent version"""
        return self.information.agent_version if self.information else None

    @property
    def host_os(self) -> Optional[str]:
        """Returns the latest host OS"""
        return self.information.host_os if self.information else None

    @property
    def status(self) -> Optional[AgentStatus]:
        """Returns the latest status record"""
        return self.status_history[-1] if self.status_history else None

    @property
    def modules(self) -> Optional[AgentModules]:
        """Returns the latest modules record"""
        return self.modules_history[-1] if self.modules_history else None

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Agent from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in display_name_history (list)
        _items = []
        if self.display_name_history:
            for _item_display_name_history in self.display_name_history:
                if _item_display_name_history:
                    _items.append(_item_display_name_history.to_dict())
            _dict['display_name_history'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in information_history (list)
        _items = []
        if self.information_history:
            for _item_information_history in self.information_history:
                if _item_information_history:
                    _items.append(_item_information_history.to_dict())
            _dict['information_history'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in status_history (list)
        _items = []
        if self.status_history:
            for _item_status_history in self.status_history:
                if _item_status_history:
                    _items.append(_item_status_history.to_dict())
            _dict['status_history'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in modules_history (list)
        _items = []
        if self.modules_history:
            for _item_modules_history in self.modules_history:
                if _item_modules_history:
                    _items.append(_item_modules_history.to_dict())
            _dict['modules_history'] = _items
        # set to None if created_by_id (nullable) is None
        # and model_fields_set contains the field
        if self.created_by_id is None and "created_by_id" in self.model_fields_set:
            _dict['created_by_id'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Agent from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "agent_identifier": obj.get("agent_identifier"),
            "display_name_history": [AgentDisplayName.from_dict(_item) for _item in obj["display_name_history"]] if obj.get("display_name_history") is not None else None,
            "information_history": [AgentInformation.from_dict(_item) for _item in obj["information_history"]] if obj.get("information_history") is not None else None,
            "status_history": [AgentStatus.from_dict(_item) for _item in obj["status_history"]] if obj.get("status_history") is not None else None,
            "modules_history": [AgentModules.from_dict(_item) for _item in obj["modules_history"]] if obj.get("modules_history") is not None else None,
            "created_by_id": obj.get("created_by_id")
        })
        return _obj
