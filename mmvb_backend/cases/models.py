from django.db import models

from common.models import FlowableModel
from django_mysql.models import JSONField, Model


def default_data():
    """Default content for case data"""
    return {}


class CaseSet(FlowableModel):
    """Case Set data model representation"""

    name = models.CharField(unique=True, max_length=200)
    # TODO: relate the case to the company which created it

    def __str__(self):
        return f"{self.name} <{self.status}>"


class Case(FlowableModel, Model):
    """Case data model representation"""

    case_sets = models.ManyToManyField("CaseSet", related_name="cases")
    data = JSONField(default=default_data)
    # TODO: relate the case to the company which created it

    def __str__(self):
        return f"{self.id} <{self.status}>"
