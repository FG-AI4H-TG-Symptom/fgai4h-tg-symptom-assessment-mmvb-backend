from enum import Enum

from django.db import models

from common.models import BaseModel
from django_mysql.models import JSONField


class BenchmarkingStepStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    ERRORED = "ERRORED"


class BenchmarkingStepError(Enum):
    TIMEOUT = "TIMEOUT"
    SERVER_ERROR = "SERVER_ERROR"
    BAD_RESPONSE = "BAD_RESPONSE"


class BenchmarkingSession(BaseModel):
    class Status(models.TextChoices):
        CREATED = "created"
        RUNNING = "running"
        INTERMEDIATE = "intermediate"
        FINISHED = "finished"

    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.CREATED,
    )
    case_set = models.ForeignKey(
        "cases.CaseSet", on_delete=models.PROTECT, related_name="+",
    )
    ai_implementations = models.ManyToManyField(
        "ai_implementations.AIImplementation", related_name="+",
    )
    task_id = models.CharField(
        max_length=50, default=None, blank=True, null=True
    )
    responses = JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} <{self.status}>"
