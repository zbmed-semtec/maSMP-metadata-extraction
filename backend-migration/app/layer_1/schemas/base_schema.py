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
    @abstractmethod
    def get_categories_of(self, property_name:str) -> str:
        ...
    
    @abstractmethod
    def get_prefixes(self) -> dict[str, str]:
        ...

    @abstractmethod
    def build_context(self) -> dict[str, str]:
        ...