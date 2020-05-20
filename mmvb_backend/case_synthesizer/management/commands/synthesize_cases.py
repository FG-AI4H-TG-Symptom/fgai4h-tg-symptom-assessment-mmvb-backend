from django.core.management.base import BaseCommand
from rest_framework.serializers import ValidationError

from case_synthesizer.exceptions import SynthesisError
from case_synthesizer.generator import generate_cases
from case_synthesizer.validators import (
    MAX_CASES_QUANTITY,
    MIN_CASES_QUANTITY,
    quantity_range,
)


class Command(BaseCommand):
    """Generates synthetic cases"""

    def add_arguments(self, parser):
        parser.add_argument("--quantity", type=int)

    def handle(self, *args, **options):
        quantity = options.get("quantity")
        quantity_validator = quantity_range(
            MIN_CASES_QUANTITY, MAX_CASES_QUANTITY
        )
        try:
            quantity_validator(quantity)
        except ValidationError as exc:
            message = str(exc.detail[0])
            self.stdout.write(
                self.style.ERROR(
                    f"Error synthesizing cases. Got a ValidationError: {message}"
                )
            )
        else:
            try:
                cases = generate_cases(quantity)
            except SynthesisError as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error synthesizing cases. Got: {str(exc)}"
                    )
                )
            else:
                cases_ids = {case.id.hex for case in cases}
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully synthesized the following "
                        f"cases {', '.join(cases_ids)}"
                    )
                )
