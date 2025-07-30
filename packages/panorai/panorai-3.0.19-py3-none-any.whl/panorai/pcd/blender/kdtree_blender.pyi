from ...data.gnomonic_image import GnomonicFace as GnomonicFace
from ..data import PCD as PCD
from ..handler import PCDHandler as PCDHandler
from .base_blender import BaseBlender as BaseBlender
from _typeshed import Incomplete

class KDTreeBlender(BaseBlender):
    merge_radius: Incomplete
    def __init__(self, merge_radius: float = 0.05, min_radius: float = 0.0, max_radius: float = 20.0, **kwargs) -> None: ...
    def process_faceset(self, faceset, model, grad_threshold: float = 0.1, feather_exp: float = 1.0): ...
