import os
import abc
import json
from typing import TypeAlias, Union
from pydantic import BaseModel

from pathlib import Path
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
PathLike = Union[str, os.PathLike, Path]


class Readable(abc.ABC):
    @abc.abstractmethod
    def read_bytes(self) -> bytes: ...

    def read_text(self, encoding: str = "utf-8") -> str:
        return self.read_bytes().decode(encoding)

    def copy_to(self, dest: PathLike) -> Path:
        dest_path = Path(str(dest))
        dest_path.write_bytes(self.read_bytes())
        return dest_path

    def read_json(self, encoding: str = "utf-8") -> JSON:
        return json.loads(self.read_text(encoding=encoding))
