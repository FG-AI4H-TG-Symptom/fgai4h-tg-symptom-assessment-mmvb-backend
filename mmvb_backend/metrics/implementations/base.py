from abc import ABC, abstractmethod
from typing import Dict, Union

from django.utils.decorators import classproperty

CalculatedResult = AggregatedResult = Dict[str, Union[str, Dict]]


class Metric(ABC):
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
    def include_as_metric(cls) -> bool:
        return NotImplementedError

    @classmethod
    @abstractmethod
    def aggregate(cls, *args, **kwargs) -> CalculatedResult:
        return NotImplementedError

    @classmethod
    @abstractmethod
    def calculate(cls, *args, **kwargs) -> AggregatedResult:
        return NotImplementedError
