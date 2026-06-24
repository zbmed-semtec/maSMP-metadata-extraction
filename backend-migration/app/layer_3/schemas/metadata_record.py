

from dataclasses import dataclass, field


@dataclass
class MetadataRecord:
    schema_name: str
    class_name: str
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_name": self.schema_name,
            "class_name": self.class_name,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MetadataRecord":
        return cls(
            schema_name=d["schema_name"], class_name=d["class_name"], data=d["data"]
        )
