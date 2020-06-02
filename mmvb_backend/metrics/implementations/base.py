from abc import ABC, abstractmethod

from django.utils.decorators import classproperty


class Metric(ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Metric:
            return True
        return False

    @classproperty
    @abstractmethod
    def name(cls) -> str:
        return NotImplementedError

    @classproperty
    @abstractmethod
    def description(cls) -> str:
        return NotImplementedError

    @classmethod
    @abstractmethod
    def aggregate(cls, *args, **kwargs):
        return NotImplementedError

    @classmethod
    @abstractmethod
    def calculate(cls, *args, **kwargs):
        return NotImplementedError
