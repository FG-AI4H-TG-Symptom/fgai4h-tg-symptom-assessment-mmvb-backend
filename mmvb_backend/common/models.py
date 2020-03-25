from uuid import uuid4

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    # TODO: add created_by and modified_by fields

    class Meta:
        abstract = True


class Company(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )


class User(AbstractUser):
    company = models.ForeignKey(
        "Company",
        related_name='users',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
