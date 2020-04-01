from django.db import transaction
from rest_framework.serializers import (
    ModelSerializer,
    JSONField,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ListField
)

from cases.models import Case, CaseSet


class CaseSetSerializer(ModelSerializer):

    class Meta:
        model = CaseSet
        fields = ["id", "name", "cases"]

    @transaction.atomic
    def create(self, validated_data):
        cases = []
        if "cases" in validated_data:
            cases = validated_data.pop("cases")
        case_set = CaseSet.objects.create(**validated_data)

        for case in cases:
            case.case_sets.add(case_set)
            case.save()

        case_set.refresh_from_db()
        return case_set

    @transaction.atomic
    def update(self, instance, validated_data):
        cases = []
        if "cases" in validated_data:
            cases = validated_data.pop("cases")
        assigned_cases = instance.cases.all()

        CaseSet.objects.filter(pk=instance.pk).update(**validated_data)

        if cases:
            for case in assigned_cases:
                if case not in cases:
                    case.case_sets.remove(instance)
            for case in cases:
                case.case_sets.add(instance)

        instance.refresh_from_db()

        return instance


class CaseSerializer(ModelSerializer):
    data = JSONField()
    case_sets = PrimaryKeyRelatedField(many=True, queryset=CaseSet.objects.all())

    class Meta:
        model = Case
        fields = ["id", "name", "data", "case_sets"]

    @transaction.atomic
    def create(self, validated_data):
        case_sets = None
        if "case_sets" in validated_data:
            case_sets = validated_data.pop("case_sets")
        case = Case.objects.create(**validated_data)

        if case_sets:
            case.case_sets.add(*case_sets)
            case.save()

        case.refresh_from_db()

        return case

    @transaction.atomic
    def update(self, instance, validated_data):
        case_sets = None
        if "case_sets" in validated_data:
            case_sets = validated_data.pop("case_sets")

        Case.objects.filter(pk=instance.pk).update(**validated_data)

        if case_sets:
            to_add = [case_set.id for case_set in case_sets]
            to_remove = [
                case_set.id for case_set in instance.case_sets.all()
                if case_set.id not in to_add
            ]
            instance.case_sets.remove(*to_remove)
            instance.case_sets.add(*to_add)

        instance.refresh_from_db()

        return instance
