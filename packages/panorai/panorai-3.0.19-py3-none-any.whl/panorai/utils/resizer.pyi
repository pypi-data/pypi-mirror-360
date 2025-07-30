import numpy as np
from _typeshed import Incomplete

logger: Incomplete
stream_handler: Incomplete

class ImageResizer:
    resize_factor: Incomplete
    method: Incomplete
    mode: Incomplete
    anti_aliasing: Incomplete
    interpolation: Incomplete
    def __init__(self, resize_factor: float = 1.0, method: str = 'skimage', mode: str = 'reflect', anti_aliasing: bool = True, interpolation: int = ...) -> None: ...
    def resize_image(self, img: np.ndarray, upsample: bool = True) -> np.ndarray: ...

class ResizerConfig:
    resize_factor: Incomplete
    method: Incomplete
    mode: Incomplete
    anti_aliasing: Incomplete
    interpolation: Incomplete
    resizer_cls: Incomplete
    def __init__(self, resizer_cls: type = ..., resize_factor: float = 1.0, method: str = 'skimage', mode: str = 'reflect', anti_aliasing: bool = True, interpolation: int = ...) -> None: ...
    def create_resizer(self) -> ImageResizer: ...
