import warnings

from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_201_CREATED

from common.utils import CamelCaseAutoSchema


class CaseSynthesizerSchema(CamelCaseAutoSchema):
    """
    Custom CamelCaseAuthoSchema for properly selecting response serializer
    and response schema
    """

    def get_response_serializer(self, path, method):
        """
        Returns the correct serializer instance defined in the view's
        `get_response_serializer` to be used in the response serialization"""
        view = self.view
        try:
            return view.get_response_serializer()
        except APIException:
            warnings.warn(
                "{}.get_custom_serializer() raised an exception during "
                "schema generation. Serializer fields will not be "
                "generated for {} {}.".format(
                    view.__class__.__name__, method, path
                )
            )

    def get_responses(self, path, method):
        """Builds up schema for documenting response"""
        self.response_media_types = self.map_renderers(path, method)

        serializer = self.get_response_serializer(path, method)
        item_schema = self._get_reference(serializer)
        response_schema = {
            "type": "array",
            "items": item_schema,
        }

        paginator = self.get_paginator()
        if paginator:
            response_schema = paginator.get_paginated_response_schema(
                response_schema
            )

        status_code = HTTP_201_CREATED
        return {
            status_code: {
                "content": {
                    ct: {"schema": response_schema}
                    for ct in self.response_media_types
                },
                "description": "",
            }
        }


class CaseSetSynthesizerSchema(CamelCaseAutoSchema):
    def get_response_serializer(self, path, method):
        """
        Returns the correct serializer instance defined in the view's
        get_response_serializer to be used in the response serialization
        """
        view = self.view
        try:
            return view.get_response_serializer()
        except APIException:
            warnings.warn(
                "{}.get_custom_serializer() raised an exception during "
                "schema generation. Serializer fields will not be "
                "generated for {} {}.".format(
                    view.__class__.__name__, method, path
                )
            )

    def get_responses(self, path, method):
        """Builds up schema for documenting response"""
        self.response_media_types = self.map_renderers(path, method)

        serializer = self.get_response_serializer(path, method)
        item_schema = self._get_reference(serializer)
        response_schema = {
            "type": "array",
            "items": item_schema,
        }

        paginator = self.get_paginator()
        if paginator:
            response_schema = paginator.get_paginated_response_schema(
                response_schema
            )

        status_code = HTTP_201_CREATED
        return {
            status_code: {
                "content": {
                    ct: {"schema": response_schema}
                    for ct in self.response_media_types
                },
                "description": "",
            }
        }
