import numpy as np
from ...utils.exceptions import ConfigurationError as ConfigurationError, TransformationError as TransformationError
from ..base.transform import BaseCoordinateTransformer as BaseCoordinateTransformer
from _typeshed import Incomplete
from typing import Any

logger: Incomplete

class GnomonicTransformer(BaseCoordinateTransformer):
    config: Incomplete
    def __init__(self, config: Any) -> None: ...
    def spherical_to_image_coords(self, lat: np.ndarray, lon: np.ndarray, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]: ...
    def projection_to_image_coords(self, x: np.ndarray, y: np.ndarray, config: Any) -> tuple[np.ndarray, np.ndarray]: ...
