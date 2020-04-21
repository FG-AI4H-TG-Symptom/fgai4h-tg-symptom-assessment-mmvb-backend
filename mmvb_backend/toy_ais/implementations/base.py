from abc import ABC, abstractmethod
from typing import Dict, List

from django.utils.decorators import classproperty


class ToyAI(ABC):

    @classmethod
    def __subclasshook__(cls, C):
        if cls is ToyAI:
            return True
        return False

    @classproperty
    @abstractmethod
    def name(cls) -> str:
        return NotImplementedError

    @classproperty
    @abstractmethod
    def slug_name(cls) -> str:
        return NotImplementedError

    @classmethod
    @abstractmethod
    def health_check(cls, *args, **kwargs):
        return NotImplementedError

    @classmethod
    @abstractmethod
    def solve_case(cls, *args, **kwargs):
        return NotImplementedError
