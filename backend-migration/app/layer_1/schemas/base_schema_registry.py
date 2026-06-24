from pathlib import Path
from abc import ABC, abstractmethod
from app.layer_1.schemas.base_schema import BaseSchema

class BaseSchemaRegistry(ABC):

    @abstractmethod
    def load(self, directory: str | Path) -> list[str]:
        ...
    
    @abstractmethod
    def get(self, name: str) -> BaseSchema:
        ...
    
    @abstractmethod
    def list(self) -> list[str]:
        ...
