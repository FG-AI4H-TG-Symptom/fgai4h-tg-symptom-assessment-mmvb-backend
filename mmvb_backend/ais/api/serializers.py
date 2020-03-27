from rest_framework.serializers import ModelSerializer

from ais.models import AIImplementation, AIImplementationEndpoint


class AIImplementationEndpointSerializer(ModelSerializer):
    class Meta:
        model = AIImplementationEndpoint
        fields = ["name", "path"]


class AIImplementationSerializer(ModelSerializer):
    endpoints = AIImplementationEndpointSerializer(many=True)

    class Meta:
        model = AIImplementation
        fields = [
            "id",
            "name",
            "base_url",
            "endpoints"
        ]

    def create(self, validated_data):
        endpoints_validated_data = validated_data.pop("endpoints")
        ai_implementation = AIImplementation.objects.create(**validated_data)

        endpoints_serializer = self.fields["endpoints"]
        for endpoint in endpoints_validated_data:
            endpoint["ai_implementation"] = ai_implementation
        endpoints = endpoints_serializer.create(endpoints_validated_data)

        return ai_implementation

    def update(self, instance, validated_data):
        endpoints_validated_data = None
        if "endpoints" in validated_data:
            endpoints_validated_data = validated_data.pop("endpoints")

        AIImplementation.objects.filter(pk=instance.pk).update(**validated_data)
        instance.refresh_from_db()

        if endpoints_validated_data:
            for data in endpoints_validated_data:
                data["ai_implementation"] = instance

                endpoint = AIImplementationEndpoint.objects.filter(
                    name=data["name"],
                    ai_implementation=instance
                )
                if endpoint:
                    endpoint.update(**data)
                else:
                    endpoint = AIImplementationEndpoint.objects.create(**data)

        return instance
