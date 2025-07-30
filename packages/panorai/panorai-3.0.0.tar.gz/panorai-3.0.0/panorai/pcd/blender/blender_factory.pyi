from .consensus_blender import EquirectangularConsensusBlender as EquirectangularConsensusBlender
from .kdtree_blender import KDTreeBlender as KDTreeBlender
from .scale_ba_blender import ScaleBundleAdjustmentBlender as ScaleBundleAdjustmentBlender
from .simple_equirect import SimpleEquirectBlender as SimpleEquirectBlender
from .voxel_blender import VoxelBlender as VoxelBlender

class PCDBlenderFactory:
    @staticmethod
    def get_blender(name: str, **kwargs): ...
