import numpy as np
from ..base.grid import BaseGridGeneration as BaseGridGeneration
from _typeshed import Incomplete

logger: Incomplete

class GnomonicGridGeneration(BaseGridGeneration):
    def projection_grid(self, delta_lat: int = 0, delta_lon: int = 0) -> tuple[np.ndarray, np.ndarray]: ...
    def spherical_grid(self, delta_lat: int = 0, delta_lon: int = 0) -> tuple[np.ndarray, np.ndarray]: ...
