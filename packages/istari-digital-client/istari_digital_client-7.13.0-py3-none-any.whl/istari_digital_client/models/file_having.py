import abc
from typing import List, Optional

from istari_digital_client.models.file import File
from istari_digital_client.models.file_revision import FileRevision
from istari_digital_client.models.file_revision_having import FileRevisionHaving


class FileHaving(FileRevisionHaving, abc.ABC):
    @property
    def _file(self) -> File:
        file = getattr(self, "file", None)

        if file is None:
            raise ValueError("file is not set")

        return file

    @property
    def revisions(self) -> List[FileRevision]:
        return self._file.revisions

    @property
    def revision(self) -> FileRevision:
        return self.revisions[-1]

    def update_properties(
        self,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        external_identifier: Optional[str] = None,
        version_name: Optional[str] = None,
    ) -> File:
        return self._file.update_properties(description, display_name, external_identifier, version_name)

    def update_description(self, description: str) -> File:
        return self._file.update_description(description)

    def update_display_name(self, display_name: str) -> File:
        return self._file.update_display_name(display_name)

    def update_external_identifier(self, external_identifier: str) -> File:
        return self._file.update_external_identifier(external_identifier)

    def update_version_name(self, version_name: str) -> File:
        return self._file.update_version_name(version_name)
