from ..blenders.registry import BlenderRegistry as BlenderRegistry
from ..projections.registry import ProjectionRegistry as ProjectionRegistry
from ..samplers.registry import SamplerRegistry as SamplerRegistry
from _typeshed import Incomplete

logger: Incomplete

class PanoraiRegistry:
    @staticmethod
    def available_samplers(): ...
    @staticmethod
    def available_blenders(): ...
    @staticmethod
    def available_projections(): ...
    @staticmethod
    def create_sampler(name: str, **kwargs): ...
    @staticmethod
    def create_blender(name: str, **kwargs): ...
    @staticmethod
    def create_projection(name: str, **kwargs): ...
