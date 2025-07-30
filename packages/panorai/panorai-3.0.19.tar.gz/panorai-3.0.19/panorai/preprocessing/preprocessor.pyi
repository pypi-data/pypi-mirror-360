import numpy as np
from .transformations import PreprocessEquirectangularImage as PreprocessEquirectangularImage
from typing import Any

class Preprocessor:
    @staticmethod
    def preprocess_eq(eq_image: np.ndarray, shadow_angle: float | None = None, delta_lat: float | None = None, delta_lon: float | None = None, resize_factor: float | None = None, resize_method: str | None = None, config: Any | None = None) -> np.ndarray: ...
