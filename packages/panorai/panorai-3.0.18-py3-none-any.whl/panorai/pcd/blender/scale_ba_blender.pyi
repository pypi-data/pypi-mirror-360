from ..data import PCD as PCD
from ..handler import PCDHandler as PCDHandler
from .base_blender import BaseBlender as BaseBlender
from _typeshed import Incomplete
from panorai.data.gnomonic_image import GnomonicFace as GnomonicFace

logger: Incomplete

def huber_loss(x, delta: float = 1.0): ...
def estimate_initial_scales_from_overlap(radius_stack, valid_stack, ref_idx: Incomplete | None = None): ...

class ScaleBundleAdjustmentBlender(BaseBlender):
    eq_shape: Incomplete
    max_iter: Incomplete
    huber_delta: Incomplete
    ref_idx: Incomplete
    def __init__(self, eq_shape=(512, 1024), min_radius: float = 0.0, max_radius: float = 20.0, match_threshold: float = 0.01, max_iter: int = 90, huber_delta: float = 1.0, ref_idx: Incomplete | None = None) -> None: ...
    def process_faceset(self, faceset, model, grad_threshold, feather_exp): ...
