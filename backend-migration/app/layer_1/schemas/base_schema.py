from abc import ABC, abstractmethod

class BaseSchema(ABC):
    @abstractmethod
    def get_schema_name(self) -> str:
        ...
    @abstractmethod
    def get_class_name(self) -> str:
        ...
    @abstractmethod
    def get_property_list(self) -> list[str]:
        ...