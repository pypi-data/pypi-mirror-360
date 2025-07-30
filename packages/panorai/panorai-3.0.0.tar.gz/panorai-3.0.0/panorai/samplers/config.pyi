from ..config.registry import ConfigRegistry as ConfigRegistry
from ..utils.exceptions import ConfigurationError as ConfigurationError
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class SamplerConfigModel(BaseModel):
    rotations: list[tuple] | None
    n_points: int | None
    model_config: Incomplete
    class Config:
        arbitrary_types_allowed: bool
        extra: str

class SamplerConfig:
    def __init__(self, **kwargs: Any) -> None: ...
    def update(self, **kwargs: Any) -> None: ...
    def __getattr__(self, item: str) -> Any: ...
    def __getitem__(self, key: str) -> Any: ...
    def __iter__(self): ...
