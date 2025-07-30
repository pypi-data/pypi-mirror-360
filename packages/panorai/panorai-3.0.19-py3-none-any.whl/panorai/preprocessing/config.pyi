from ..config.registry import ConfigRegistry as ConfigRegistry
from ..utils.exceptions import ConfigurationError as ConfigurationError
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

ConfigDict = dict
logger: Incomplete

class PreprocessorConfigModel(BaseModel):
    shadow_angle: float
    delta_lat: float
    delta_lon: float
    resize_factor: float
    resize_method: str
    def validate_resize_factor(cls, v): ...
    model_config: Incomplete

class PreprocessorConfig:
    def __init__(self, **kwargs: Any) -> None: ...
    def update(self, **kwargs: Any) -> None: ...
    def __getattr__(self, item: str) -> Any: ...
    def __getitem__(self, key: str) -> Any: ...
    def __iter__(self): ...
