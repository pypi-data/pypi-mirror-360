import numpy as np
from ...utils.exceptions import GridGenerationError as GridGenerationError, ProcessingError as ProcessingError
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class BaseGridGeneration:
    config: Incomplete
    def __init__(self, config: Any) -> None: ...
    def projection_grid(self) -> tuple[np.ndarray, np.ndarray]: ...
