import numpy as np
from ..utils.exceptions import ConfigurationError as ConfigurationError, ProcessingError as ProcessingError
from .base.interpolation import BaseInterpolation as BaseInterpolation
from .gnomonic.config import GnomonicConfig as GnomonicConfig
from .gnomonic.grid import GnomonicGridGeneration as GnomonicGridGeneration
from .gnomonic.strategy import GnomonicProjectionStrategy as GnomonicProjectionStrategy
from .gnomonic.transform import GnomonicTransformer as GnomonicTransformer
from .registry import ProjectionRegistry as ProjectionRegistry
from _typeshed import Incomplete

class GnomonicProjection:
    config: Incomplete
    grid_generator: Incomplete
    strategy: Incomplete
    transformer: Incomplete
    interpolation: Incomplete
    def __init__(self, config: GnomonicConfig | None = None, phi1_deg: float = 0.0, lam0_deg: float = 0.0, fov_deg: float = 90.0, **kwargs) -> None: ...
    def project(self, eq_img: np.ndarray) -> np.ndarray: ...
    def back_project(self, face_img: np.ndarray, eq_shape: tuple[int, int]) -> np.ndarray: ...
