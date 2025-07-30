import numpy as np
from ..blenders.registry import BlenderRegistry as BlenderRegistry
from ..config.config_manager import ConfigManager as ConfigManager
from ..data.equirectangular_image import EquirectangularImage as EquirectangularImage
from ..data.factory import DataFactory as DataFactory
from ..data.gnomonic_image import GnomonicFace as GnomonicFace
from ..data.gnomonic_imageset import GnomonicFaceSet as GnomonicFaceSet
from ..projections.registry import ProjectionRegistry as ProjectionRegistry
from ..samplers.registry import SamplerRegistry as SamplerRegistry
from .exceptions import BlenderNotFoundError as BlenderNotFoundError, ConfigNotFoundError as ConfigNotFoundError, ProjectionNotFoundError as ProjectionNotFoundError, SamplerNotFoundError as SamplerNotFoundError
from PIL import Image as Image
from _typeshed import Incomplete
from typing import Literal

logger: Incomplete

class PanoraiFactory:
    @classmethod
    def modify_config(cls, name: str, **kwargs) -> None: ...
    @classmethod
    def describe_config(cls, name: str) -> None: ...
    @classmethod
    def load_image(cls, file_path: str, data_type: Literal['equirectangular', 'gnomonic_face'] = 'equirectangular') -> EquirectangularImage: ...
    @classmethod
    def create_data_from_array(cls, data: np.ndarray, data_type: str, **kwargs) -> EquirectangularImage | GnomonicFace: ...
    @classmethod
    def get_sampler(cls, name: str, **kwargs): ...
    @classmethod
    def get_blender(cls, name: str, **kwargs): ...
    @classmethod
    def get_projection(cls, name: str, lat: float, lon: float, fov: float, **kwargs): ...
    @classmethod
    def reset_all(cls) -> None: ...
    @classmethod
    def list_available(cls) -> None: ...
