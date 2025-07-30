from .base_blenders import BaseBlender as BaseBlender
from .registry import BlenderRegistry as BlenderRegistry

class OverlapCounterBlender(BaseBlender):
    def blend(self, images, masks, **kwargs): ...
