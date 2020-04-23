import warnings

from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_201_CREATED

from common.utils import CamelCaseAutoSchema


class CaseSynthesizerSchema(CamelCaseAutoSchema):
    def get_response_serializer(self, path, method):
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
