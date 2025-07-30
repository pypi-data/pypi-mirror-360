import abc
from ..data import PCD as PCD
from _typeshed import Incomplete
from abc import ABC, abstractmethod

class BaseBlender(ABC, metaclass=abc.ABCMeta):
    min_radius: Incomplete
    max_radius: Incomplete
    def __init__(self, min_radius: float = 0.0, max_radius: float = 20.0) -> None: ...
    @abstractmethod
    def process_faceset(self, faceset, model, grad_threshold: float = 0.1, feather_exp: float = 2.0): ...
    @staticmethod
    def compute_radius(depth, u, v): ...
