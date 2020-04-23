# Generated by Django 3.0.4 on 2020-04-01 08:54

import uuid

import cases.models
import django_mysql.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CaseSet",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("submitted", "Submitted"),
                            ("reviewing", "Reviewing"),
                            ("adjusting", "Adjusting"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("published", "Published"),
                        ],
                        default="created",
                        max_length=50,
                    ),
                ),
                ("public", models.NullBooleanField(default=False)),
                ("name", models.CharField(max_length=200, unique=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Case",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("submitted", "Submitted"),
                            ("reviewing", "Reviewing"),
                            ("adjusting", "Adjusting"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("published", "Published"),
                        ],
                        default="created",
                        max_length=50,
                    ),
                ),
                ("public", models.NullBooleanField(default=False)),
                ("name", models.CharField(max_length=150, unique=True)),
                (
                    "data",
                    django_mysql.models.JSONField(default=cases.models.default_data),
                ),
                (
                    "case_sets",
                    models.ManyToManyField(related_name="cases", to="cases.CaseSet"),
                ),
            ],
            options={"abstract": False},
        ),
    ]
