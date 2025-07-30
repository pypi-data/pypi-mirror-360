import abc
from abc import ABC, abstractmethod
from typing import Any

class BaseBlender(ABC, metaclass=abc.ABCMeta):
    params: dict[str, Any]
    def __init__(self, **kwargs: Any) -> None: ...
    @abstractmethod
    def blend(self, images, masks): ...
    def update(self, **kwargs) -> None: ...
