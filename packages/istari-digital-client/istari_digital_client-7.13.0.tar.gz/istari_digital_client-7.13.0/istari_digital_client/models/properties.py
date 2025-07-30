import abc
from functools import cached_property
from pathlib import Path

import istari_digital_core


class Properties:
    """Class for holding file properties.

    Properties are the information about a file that's not it's actual content
    but the information stored on a filesystem *about* the file.

    Things like the file name, size, mime type, description, etc...
    """

    def __init__(self: "Properties", native: istari_digital_core.Properties) -> None:
        self.native: istari_digital_core.Properties = native

    @cached_property
    def name(self: "Properties") -> str:
        """The objects file name.

        This includes the extension.

        For example:
        > x.name
        "foo.JPG"
        > x.stem
        "foo"
        > x.extension
        "jpg"
        > x.suffix
        ".JPG"
        """
        file_name = str(self.native.file_name)
        if file_name.lower().endswith(f".{self.extension}"):
            return file_name
        return ".".join([file_name, self.extension])

    @cached_property
    def stem(self: "Properties") -> str:
        """The objects file name stem.

        The stem is the file name without the suffix.

        For example:
        > x.stem
        "foo"
        > x.name
        "foo.jpg"
        > x.extension
        "jpg"
        """
        return Path(self.name).stem

    @property
    def size(self: "Properties") -> int:
        """The objects file size"""
        return self.native.size

    @property
    def mime_type(self: "Properties") -> str:
        """The mime type of the objects file (if known)"""
        return str(self.native.mime)

    @cached_property
    def suffix(self) -> str:
        """Returns the file name suffix.

        - preserves original casing
        - includes the "."

        Examples:
        > x.name
        "foo.JPG"
        > x.suffix
        ".JPG"
        > x.extension
        "jpg"
        """
        return Path(self.name).suffix

    @property
    def extension(self: "Properties") -> str:
        """The objects file name extension.
        Will always be lower case
        Does not include the ".".

        For example:
        > x.extension
        "jpg"
        > x.name
        "foo.JPG"
        > x.stem
        "foo"
        """
        return self.native.extension.lower()

    @property
    def description(self: "Properties") -> str | None:
        """The description set in the file properties.

        Will return None if not set.
        """

        return self.native.description or None

    @property
    def version_name(self: "Properties") -> str | None:
        """The version name set in the file properties.

        Will return None if not set
        """

        return self.native.version_name or None

    @property
    def external_identifier(self: "Properties") -> str | None:
        """The external identifier set in the file properties.

        Will return None if not set
        """
        return self.native.external_identifier or None

    @property
    def display_name(self: "Properties") -> str | None:
        """The display name set in the file properties.

        Will return None if not set
        """
        return self.native.display_name or None


class PropertiesHaving(abc.ABC):
    @property
    @abc.abstractmethod
    def properties(self: "PropertiesHaving") -> "Properties": ...

    @property
    def extension(self: "PropertiesHaving") -> str:
        return self.properties.extension

    @property
    def name(self: "PropertiesHaving") -> str:
        return self.properties.name

    @property
    def stem(self: "PropertiesHaving") -> str:
        return self.properties.stem

    @property
    def description(self: "PropertiesHaving") -> str | None:
        return self.properties.description

    @property
    def size(self: "PropertiesHaving") -> int:
        return self.properties.size

    @property
    def mime_type(self: "PropertiesHaving") -> str:
        return self.properties.mime_type

    @property
    def version_name(self: "PropertiesHaving") -> str | None:
        return self.properties.version_name

    @property
    def external_identifier(self: "PropertiesHaving") -> str | None:
        return self.properties.external_identifier

    @property
    def display_name(self: "PropertiesHaving") -> str | None:
        return self.properties.display_name
