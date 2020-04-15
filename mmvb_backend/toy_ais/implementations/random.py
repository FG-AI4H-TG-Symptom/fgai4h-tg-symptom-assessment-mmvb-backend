from typing import Dict, List
from .base import ToyAI

from django.utils.decorators import classproperty


class UniformRandomConditions(ToyAI):

    @classproperty
    def name(cls) -> str:
        return "Uniform Random Conditions Solver"

    @classproperty
    def slug_name(cls) -> str:
        return "uniform-random-conditions"

    @classmethod
    def health_check(cls, *args, **kwargs):
        return {"data": f"OK from {cls.name}"}

    @classmethod
    def solve_case(cls, payload, *args, **kwargs):
        pass


class WeightedRandomConditions(ToyAI):

    @classproperty
    def name(cls) -> str:
        return "Weighted Random Conditions Solver"

    @classproperty
    def slug_name(cls) -> str:
        return "weighted-random-conditions"

    @classmethod
    def health_check(cls, *args, **kwargs):
        return {"data": f"OK from {cls.name}"}

    @classmethod
    def solve_case(cls, payload, *args, **kwargs):
        pass
