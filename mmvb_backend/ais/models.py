from django.db import models

from common.models import BaseModel


class AIImplementation(BaseModel):
    # TODO: implement character validation for fields
    name = models.CharField(unique=True, max_length=50)
    base_url = models.URLField()

    def __str__(self):
        return self.name


class AIImplementationEndpoint(models.Model):
    META = "meta"
    METRICS = "metrics"

    ENDPOINT_OPTIONS = (
        (META, "Meta"),
        (METRICS, "Metrics"),
    )

    # TODO: implement character validation for fields
    name = models.CharField(max_length=30, choices=ENDPOINT_OPTIONS)
    path = models.CharField(max_length=150)
    ai_implementation = models.ForeignKey(
        "AIImplementation", related_name="endpoints", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "ai_implementation"], name="unique_ai_endpoint"
            )
        ]
