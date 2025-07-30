import numpy as np
from ...utils.exceptions import InterpolationError as InterpolationError
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class BaseInterpolation:
    config: Incomplete
    def __init__(self, config: Any) -> None: ...
    def interpolate(self, input_img: np.ndarray, map_x: np.ndarray, map_y: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray: ...
