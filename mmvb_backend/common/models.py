from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models

# TODO: (Future) those states should be decided upon for proper
# TODO: (Future) implementation of the reviewing flow when publishing
# TODO: (Future) cases
CREATED = "created"
SUBMITTED = "submitted"
REVIEWING = "reviewing"
ADJUSTING = "adjusting"
APPROVED = "approved"
REJECTED = "rejected"
PUBLISHED = "published"

STATUS_OPTIONS = (
    (CREATED, "Created"),
    (SUBMITTED, "Submitted"),
    (REVIEWING, "Reviewing"),
    (ADJUSTING, "Adjusting"),
    (APPROVED, "Approved"),
    (REJECTED, "Rejected"),
    (PUBLISHED, "Published"),
)


class BaseModel(models.Model):
    """
    Abstract base data model that uses uuid as identifier and includes
    created and modified data fields
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    # TODO: add created_by and modified_by fields

    class Meta:
        abstract = True


class FlowableModel(models.Model):
    """
    Abstract base model that uses uuid as identifier and includes fields
    for tracking status and publicity of concrete data model
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # dates are needed for these models
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=50, choices=STATUS_OPTIONS, default=CREATED
    )
    public = models.NullBooleanField(default=False)

    class Meta:
        abstract = True

    # TODO: implement flow states transition handling


class Company(BaseModel):
    """
    Initial data model representation for Company that is part of the
    Symptom Assessment (WHO/ITU) group
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)


class User(AbstractUser):
    """
    Custom User data model representation
    """

    company = models.ForeignKey(
        "Company",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
