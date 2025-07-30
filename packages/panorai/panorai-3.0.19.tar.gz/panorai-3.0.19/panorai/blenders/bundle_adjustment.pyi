from .base_blenders import BaseBlender as BaseBlender
from .registry import BlenderRegistry as BlenderRegistry
from _typeshed import Incomplete

logger: Incomplete

class BundleAdjustmentBlender(BaseBlender):
    def blend(self, images, masks, delta: float = 1.0, **kwargs): ...
