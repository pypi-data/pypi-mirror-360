import numpy as np
from ...utils.exceptions import ProcessingError as ProcessingError
from ..base.strategy import BaseProjectionStrategy as BaseProjectionStrategy
from .config import GnomonicConfig as GnomonicConfig
from _typeshed import Incomplete

logger: Incomplete

class GnomonicProjectionStrategy(BaseProjectionStrategy):
    config: Incomplete
    def __init__(self, config: GnomonicConfig) -> None: ...
    def from_projection_to_spherical(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...
    def from_spherical_to_projection(self, lat: np.ndarray, lon: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
