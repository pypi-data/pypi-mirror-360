
from __future__ import annotations
import pprint
import re  # noqa: F401
import json
import uuid

import datetime
from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List
from typing import Optional, Set
from typing_extensions import Self

import istari_digital_core


class Token(BaseModel):
    """
    :class:`Token` is a subclass of :class:`Base` and represents a token used to store file information.
    """ # noqa: E501
    id: StrictStr
    created: datetime.datetime
    sha: StrictStr
    salt: StrictStr
    created_by_id: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["id", "created", "sha", "salt", "created_by_id"]

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
        """Create an instance of Token from a JSON string"""
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

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Token from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "sha": obj.get("sha"),
            "salt": obj.get("salt"),
            "created_by_id": obj.get("created_by_id")
        })
        return _obj

    @classmethod
    def from_storage_token(
        cls,
        storage_token: istari_digital_core.Token,
    ) -> Self:
        return cls(
            id=str(uuid.uuid4()),
            created=datetime.datetime.now(datetime.timezone.utc),
            sha=storage_token.sha,
            salt=storage_token.salt,
        )

    @classmethod
    def compare_token(
        cls,
        sha: str,
        salt: str,
        data: bytes,
    ) -> None:
        """Compare the token with the data and raise an exception if they do not match."""
        try:
            istari_digital_core.Token.compare_token(sha, salt, data)
        except ValueError as e:
            raise ValueError("Token does not match the data") from e

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        salt: str | None = None,
    ) -> Self:
        """Create a Token from bytes and salt."""
        return cls.from_storage_token(istari_digital_core.Token.from_bytes(data, salt))
