from ..data import PCD as PCD
from ..handler import PCDHandler as PCDHandler
from .base_blender import BaseBlender as BaseBlender
from _typeshed import Incomplete
from panorai.data.gnomonic_image import GnomonicFace as GnomonicFace

class EquirectangularConsensusBlender(BaseBlender):
    eq_shape: Incomplete
    smooth_sigma: Incomplete
    def __init__(self, eq_shape=(512, 1024), min_radius: float = 0.0, max_radius: float = 20.0, smooth_sigma: float = 1.0) -> None: ...
    def process_faceset(self, faceset, model, grad_threshold, feather_exp): ...
