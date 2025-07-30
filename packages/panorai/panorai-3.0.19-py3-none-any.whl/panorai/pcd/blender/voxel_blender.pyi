from .base_blender import BaseBlender as BaseBlender
from _typeshed import Incomplete
from panorai.data.gnomonic_image import GnomonicFace as GnomonicFace
from panorai.pcd.data import PCD as PCD
from panorai.pcd.handler import PCDHandler as PCDHandler

class VoxelBlender(BaseBlender):
    voxel_size: Incomplete
    def __init__(self, voxel_size: float = 0.005, min_radius: float = 0.0, max_radius: float = 5.0, **kwargs) -> None: ...
    def process_faceset(self, faceset, model, grad_threshold, feather_exp): ...
