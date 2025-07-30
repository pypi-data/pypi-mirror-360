import abc
from .config import SamplerConfig as SamplerConfig
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from typing import Any

class Sampler(ABC, metaclass=abc.ABCMeta):
    config: Incomplete
    def __init__(self, config: SamplerConfig | None = None, **kwargs: Any) -> None: ...
    @abstractmethod
    def get_tangent_points(self) -> list[tuple[float, float]]: ...
    def update(self, **kwargs: Any) -> None: ...
