from django.db import models

from common.models import BaseModel


class AIImplementation(BaseModel):
    # TODO: implement character validation for fields
    name = models.CharField(unique=True, max_length=50)
    base_url = models.URLField()
    health_endpoint = models.CharField(max_length=30)
    solution_endpoint = models.CharField(max_length=50)

    def __str__(self):
        return self.name
