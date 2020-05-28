from uuid import uuid4

from django.conf import settings
from rest_framework.schemas.openapi import AutoSchema

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from stringcase import camelcase

DEFAULT_TIMEOUT = settings.DEFAULT_TIMEOUT
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504, 400],
    method_whitelist=["HEAD", "GET", "OPTIONS"],
)


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


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


def perform_request(url):
    adapter = TimeoutHTTPAdapter()
    http = requests.Session()

    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url)
    except Exception as exc:
        response = {
            "detail": f"Error trying to perform request. Got {str(exc)}"
        }
    return response
