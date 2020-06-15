from abc import ABC, abstractmethod
from typing import Dict, Union

from django.utils.decorators import classproperty

# typing definition for metrics results
CalculatedResult = AggregatedResult = Dict[str, Union[str, Dict]]


class Metric(ABC):
    """Abstract base class for defining an interface for implementing Metric"""

    @classproperty
    @abstractmethod
    def name(cls) -> str:
        """Abstract class property for returning the public name of the Metric"""
        raise NotImplementedError

    @classproperty
    @abstractmethod
    def description(cls) -> str:
        """
        Abstract class property for returning the public description of the Metric
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def include_as_metric(cls) -> bool:
        """
        Abstract class method informing if the class should be considered an
        available Metric
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def aggregate(cls, *args, **kwargs) -> CalculatedResult:
        """
        Abstract class method for aggregating the metrics of a benchmark result
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calculate(cls, *args, **kwargs) -> AggregatedResult:
        """
        Abstract class method for calculating the metrics on a benchmark result
        """
        raise NotImplementedError
