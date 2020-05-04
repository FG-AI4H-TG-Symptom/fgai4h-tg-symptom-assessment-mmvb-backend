from rest_framework.serializers import ValidationError

MIN_QUANTITY = 1
MAX_QUANTITY = 200


def quantity_range(value):
    value = int(value)
    if value > MAX_QUANTITY or value < MIN_QUANTITY:
        raise ValidationError(
            f"Invalid value {value}. It must be within "
            f"{MIN_QUANTITY} and {MAX_QUANTITY}."
        )
