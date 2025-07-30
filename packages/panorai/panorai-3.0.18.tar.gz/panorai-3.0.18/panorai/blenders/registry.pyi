from _typeshed import Incomplete
from functools import wraps as wraps
from typing import Any

logger: Incomplete

class BlenderRegistry:
    @classmethod
    def register(cls, name: str): ...
    @classmethod
    def create(cls, name: str, **kwargs: Any): ...
    @classmethod
    def available_blenders(cls) -> list: ...
