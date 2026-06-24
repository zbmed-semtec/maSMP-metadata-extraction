import json
from layer_1.schemas.metadata_record import MetadataRecord

class MetadataSerializer:
    def __init__(self, registry):
        self.registry = registry

    def to_json(self, record: MetadataRecord) -> str:
        return json.dumps(record.to_dict(), indent=2)

    def from_json(self, json_str: str) -> MetadataRecord:
        return MetadataRecord.from_dict(json.loads(json_str))

    def to_dict(self, record: MetadataRecord) -> dict:
        return record.to_dict()