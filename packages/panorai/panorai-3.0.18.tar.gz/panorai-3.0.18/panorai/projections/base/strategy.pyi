import numpy as np
from ...utils.exceptions import ProcessingError as ProcessingError
from _typeshed import Incomplete

logger: Incomplete

class BaseProjectionStrategy:
    @classmethod
    def from_spherical_to_projection(cls, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...
    @classmethod
    def from_projection_to_spherical(cls, lat: np.ndarray, lon: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
