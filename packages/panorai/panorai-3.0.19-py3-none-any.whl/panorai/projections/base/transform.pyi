import numpy as np
from ...utils.exceptions import TransformationError as TransformationError
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class BaseCoordinateTransformer:
    config: Incomplete
    def __init__(self, config: Any) -> None: ...
    @classmethod
    def spherical_to_image_coords(cls, lat: np.ndarray, lon: np.ndarray, config: Any, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]: ...
    @staticmethod
    def projection_to_image_coords(x: np.ndarray, y: np.ndarray, config: Any) -> tuple[np.ndarray, np.ndarray]: ...
