from _typeshed import Incomplete

logger: Incomplete

class RegistryBase(type):
    REGISTRY: dict[str, type]
    def __new__(cls, name, bases, attrs): ...
    @classmethod
    def get_registry(cls) -> dict[str, type]: ...

class BaseRegisteredClass(metaclass=RegistryBase): ...
