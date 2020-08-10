from django.db import models

from common.models import BaseModel


class AIImplementation(BaseModel):
    """AI Implementation data model representation"""

    # TODO: implement character validation for fields
    name = models.CharField(unique=True, max_length=50)
    base_url = models.URLField()

    def __str__(self):
        return self.name
