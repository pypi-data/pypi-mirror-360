import numpy as np
from _typeshed import Incomplete

class ImageResizer:
    resize_factor: Incomplete
    method: Incomplete
    mode: Incomplete
    anti_aliasing: Incomplete
    interpolation: Incomplete
    def __init__(self, resize_factor: float = 1.0, method: str = 'skimage', mode: str = 'reflect', anti_aliasing: bool = True, interpolation: int = ...) -> None: ...
    def resize_image(self, img: np.ndarray) -> np.ndarray: ...

class PreprocessEquirectangularImage:
    @classmethod
    def extend_height(cls, image: np.ndarray, shadow_angle: float) -> np.ndarray: ...
    @classmethod
    def undo_extend_height(cls, extended_image: np.ndarray, shadow_angle: float) -> np.ndarray: ...
    @classmethod
    def rotate(cls, image: np.ndarray, delta_lat: float, delta_lon: float) -> np.ndarray: ...
    @classmethod
    def preprocess(cls, image: np.ndarray, **kwargs) -> np.ndarray: ...
