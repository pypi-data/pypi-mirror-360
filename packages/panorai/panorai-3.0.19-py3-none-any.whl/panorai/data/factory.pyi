import numpy as np
from .equirectangular_image import EquirectangularImage as EquirectangularImage
from .gnomonic_image import GnomonicFace as GnomonicFace
from .gnomonic_imageset import GnomonicFaceSet as GnomonicFaceSet
from PIL import Image
from _typeshed import Incomplete
from typing import Literal

class DataFactory:
    data: Incomplete
    def __init__(self, data: EquirectangularImage | GnomonicFace | GnomonicFaceSet) -> None: ...
    @classmethod
    def from_array(cls, data: np.ndarray, data_type: str) -> EquirectangularImage | GnomonicFace: ...
    @classmethod
    def from_dict(cls, data: dict[str, np.ndarray], data_type: str) -> EquirectangularImage | GnomonicFace: ...
    @classmethod
    def from_list(cls, faces: list[GnomonicFace], channel_name: str = 'default') -> GnomonicFaceSet: ...
    @classmethod
    def from_pil(cls, img: Image.Image, data_type: str) -> EquirectangularImage | GnomonicFace: ...
    @classmethod
    def from_file(cls, file_path: str, data_type: Literal['equirectangular', 'gnomonic_face']) -> EquirectangularImage | GnomonicFace: ...
