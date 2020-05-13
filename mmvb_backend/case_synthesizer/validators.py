from rest_framework.serializers import ValidationError

MIN_CASES_QUANTITY = 1
MAX_CASES_QUANTITY = 200
MIN_CASESETS_QUANTITY = 1
MAX_CASESETS_QUANTITY = 10


def quantity_range(lower_limit, upper_limit):
    def validator(value):
        value = int(value)
        if value > upper_limit or value < lower_limit:
            raise ValidationError(
                f"Invalid value {value}. It must be within "
                f"{lower_limit} and {upper_limit}."
            )
    return validator
