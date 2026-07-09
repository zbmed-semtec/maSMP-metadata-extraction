from dataclasses import dataclass
from typing import Any

@dataclass
class MetadataProperty[T]:
    source: str
    property_name: str
    property_value: T
    confidence: float = 1.0

class MetadataCollector:
    data : dict[str, dict[str, MetadataProperty]]

    def __init__(self):
        self.data = {}
    
    def collect(self, source: str, property_name: str, property_value: Any, confidence:float=1.0):
        if not property_name in self.data:
            self.data[property_name] = {}
        all_records = self.data[property_name]
        all_records[source] = MetadataProperty(source, property_name, property_value, confidence)
        self.data[property_name] = all_records
    
    def get(self, property_name: str, source: str = None, default: Any = None) -> dict[str, Any] | Any:
        all_records = self.data.get(property_name, dict())
        if source is None:
            return all_records
        return all_records.get(source, default)
    
    def get_most_confident(self, uri: str) -> MetadataProperty[Any]:
        all = self.data.get(uri, dict())
        values = sorted(all.values(), key=lambda x : x.confidence, reverse=True)
        try:
            return values[0]
        except:
            return None
