import importlib
import pkgutil
import re
import sys
from json import JSONDecodeError
from uuid import uuid4

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.status import HTTP_200_OK
from stringcase import camelcase

from common.definitions import HealthCheckStatus

DEFAULT_TIMEOUT = settings.DEFAULT_TIMEOUT
DEFAULT_MAX_RETRIES = settings.MAX_RETRIES


class CamelCaseAutoSchema(AutoSchema):
    """
    Custom AutoSchema to properly perform snake_case to CamelCase
    conversion of serialized data for the API endpoints requests/responses
    """

    def map_serializer(self, serializer):
        """Performs camelcase conversion for properties of serialised data"""
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
    """Evaluates if a given value is true or false"""
    return settings.IS_TRUE(value)


def generate_id():
    """Generates a UUID"""
    return uuid4()


def get_all_subclasses(cls):
    """Gets all subclasses of a given class or its subclasses"""
    all_subclasses = set(cls.__subclasses__()).union(
        [
            sub
            for klass in cls.__subclasses__()
            for sub in get_all_subclasses(klass)
        ]
    )

    subclasses = []

    for klass in all_subclasses:
        if (
            not hasattr(klass, "include_as_metric")
            or klass.include_as_metric()
        ):
            subclasses.append(klass)
    return subclasses


def char_to_digit(text):
    """
    Converts text to integer if it contains a number else returns the text
    """
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    Filters strings to find numbers and convert them to integers.
    It can be used for sorting strings containing integers to avoid
    situations where `something1`, `something12`, `something2`
    will be sorted like that when the expected sorting would be
    `something1`, `something2`, `something12`
    """
    return [char_to_digit(c) for c in re.split(r"(\d+)", text)]


def import_modules(package_name):
    """Dynamically imports submodules"""
    exclude = {"base", "utils"}

    package = sys.modules[package_name]
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if name not in exclude:
            importlib.import_module(package_name + "." + name)


def perform_request(url, retries=DEFAULT_MAX_RETRIES, timeout=DEFAULT_TIMEOUT):
    """
    Performs a http GET request to a given url respecting the maximum amount
    of retries and the specified timeout
    """
    adapter = HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    response = {"status": "", "data": None, "detail": ""}

    try:
        request_response = session.get(url, timeout=timeout)
    except ConnectionError as exc:
        response["status"] = HealthCheckStatus.TIMEOUT.value
        response["detail"] = f"Error trying to perform request. Got {str(exc)}"
    except Exception as exc:
        response["status"] = HealthCheckStatus.BAD_RESPONSE.value
        response["detail"] = f"Error trying to perform request. Got {str(exc)}"
    else:
        if request_response.status_code != HTTP_200_OK:
            response["status"] = HealthCheckStatus.BAD_RESPONSE.value
            response[
                "detail"
            ] = f"Error on health check response. Got HTTP {request_response.status_code}"
        else:
            response["status"] = HealthCheckStatus.OK.value

        try:
            response["data"] = request_response.json()
        except JSONDecodeError:
            response["status"] = HealthCheckStatus.BAD_RESPONSE.value
            response["data"] = "Error trying to parse response (invalid JSON)"

    return response


def change_keys(obj, convert):
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = change_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(change_keys(v, convert) for v in obj)
    else:
        return obj
    return new
