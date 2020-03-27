from django.db import models

from common.models import FlowableModel


def default_data():
    return {}


class CaseSet(FlowableModel):
    name = models.CharField(unique=True, max_length=200)
    # TODO: relate the case to the company which created it

    def __str__(self):
        return f"{self.name} <{status}>"


class Case(FlowableModel):
    name = models.CharField(unique=True, max_length=150)
    case_sets = models.ManyToManyField(
        "CaseSet",
        related_name="cases",
    )
    # TODO: relate the case to the company which created it

    def __str__(self):
        return f"{self.name} <{status}>"
