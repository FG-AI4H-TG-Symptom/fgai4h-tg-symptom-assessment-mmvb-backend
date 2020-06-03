import importlib
import pkgutil
import re
import sys
from uuid import uuid4

from rest_framework.schemas.openapi import AutoSchema

from stringcase import camelcase


class CamelCaseAutoSchema(AutoSchema):
    def map_serializer(self, serializer):
        result = super().map_serializer(serializer)
        camelized_properties = {
            camelcase(field_name): schema
            for field_name, schema in result["properties"].items()
        }
        new_result = {"type": "object", "properties": camelized_properties}
        if "required" in result:
            new_result["required"] = list(map(camelcase, result["required"]))

        return new_result


def is_true(value):
    return str(value).lower() in ["1", "true", "yes"]


def generate_id():
    return uuid4()


def get_all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [
            sub
            for klass in cls.__subclasses__()
            for sub in get_all_subclasses(klass)
        ]
    )


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def import_modules(package_name):
    """Dynamically imports submodules"""
    exclude = {"base", "utils"}

    package = sys.modules[package_name]
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if name not in exclude:
            importlib.import_module(package_name + "." + name)
