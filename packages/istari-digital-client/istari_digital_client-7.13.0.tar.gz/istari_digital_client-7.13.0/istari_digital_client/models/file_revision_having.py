import abc
from pydantic import BaseModel

from istari_digital_client.models.file_revision import FileRevision
from istari_digital_client.models.readable import Readable
from istari_digital_client.models.properties import Properties


class FileRevisionHaving(BaseModel, Readable, abc.ABC):
    @property
    @abc.abstractmethod
    def revision(self) -> FileRevision: ...

    def read_bytes(self) -> bytes:
        return self.revision.read_bytes()

    @property
    def properties(self) -> Properties:
        return self.revision.properties

    @property
    def extension(self) -> str | None:
        return self.revision.extension

    @property
    def name(self) -> str | None:
        if self.revision.name is None or self.extension is None:
            return None

        file_name = self.revision.name
        if file_name.lower().endswith(f".{self.extension}"):
            return file_name
        return ".".join([file_name, self.extension])

    @property
    def stem(self) -> str | None:
        return self.revision.stem

    @property
    def suffix(self) -> str | None:
        return self.revision.suffix

    @property
    def description(self) -> str | None:
        return self.revision.description

    @property
    def size(self) -> int | None:
        return self.revision.size

    @property
    def mime(self) -> str | None:
        return self.revision.mime

    @property
    def version_name(self) -> str | None:
        return self.revision.version_name

    @property
    def external_identifier(self) -> str | None:
        return self.revision.external_identifier

    @property
    def display_name(self) -> str | None:
        return self.revision.display_name
