from abc import ABC, abstractmethod

from django.utils.decorators import classproperty


class ToyAI(ABC):
    """Abstract base class for defining an interface for implementing Toy AIs"""

    @classproperty
    @abstractmethod
    def name(cls) -> str:
        """Abstract class property for returning the public name of the Toy AI"""
        raise NotImplementedError

    @classproperty
    @abstractmethod
    def slug_name(cls) -> str:
        """
        Abstract class property for returning the public slug name (url path)
        of the Toy AI
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def health_check(cls, *args, **kwargs):
        """Abstract class method for performing a health check"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def solve_case(cls, *args, **kwargs):
        """Abstract class method for performing a case solving"""
        raise NotImplementedError
