
from abc import ABC, abstractmethod
from os import urandom
from re import search
from typing import Dict
from uuid import UUID


class ConfigObject(ABC):

    @property
    @abstractmethod
    def coid(self):
        pass
    
    @abstractmethod
    def toJSON(self) -> Dict:
        return { "__coid" : str(self.coid) }

class ConfigObjectIdentifier(ABC, UUID):
    
    @classmethod
    def matches(cls, coid: str) -> bool:

        if match := search(ConfigObjectIdentifier._COID_REGEX, coid):
            return match.group('object_type') == cls._object_type()
        
        return False

    @abstractmethod
    def inflate_data(self, data: dict) -> ConfigObject:
        pass
    
    @staticmethod
    @abstractmethod
    def _object_type() -> str:
        pass

    def __init__(self, coid: str=None) -> None:
        if coid is None:
            return super().__init__(bytes=urandom(16), version=4)
        
        if match := search(ConfigObjectIdentifier._COID_REGEX, coid):
            return super().__init__(match.group('uuid'), version=4)
        
        raise ValueError(f"COID is invalid: {coid}")

    _COID_REGEX = r'<(?P<object_type>.+)>(?P<uuid>[\w]{8}-(?:[\w]{4}-){3}[\w]{12})'

    def __str__(self) -> str:
        return f"<{self._object_type()}>{super().__str__()}"
