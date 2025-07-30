import dataclasses


@dataclasses.dataclass
class NewSource:
    revision_id: str
    relationship_identifier: str | None = None
