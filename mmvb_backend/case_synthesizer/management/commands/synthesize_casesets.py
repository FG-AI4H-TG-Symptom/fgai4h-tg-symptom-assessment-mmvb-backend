from django.core.management.base import BaseCommand
from rest_framework.serializers import ValidationError

from case_synthesizer.exceptions import SynthesisError
from case_synthesizer.generator import generate_casesets
from case_synthesizer.validators import (
    MAX_CASES_QUANTITY,
    MAX_CASESETS_QUANTITY,
    MIN_CASES_QUANTITY,
    MIN_CASESETS_QUANTITY,
    quantity_range,
)


class Command(BaseCommand):
    """Generates synthetic case sets with synthetic cases"""

    def add_arguments(self, parser):
        parser.add_argument("--quantity_of_casesets", type=int)
        parser.add_argument("--cases_per_caseset", type=int)

    def handle(self, *args, **options):
        quantity_of_casesets = options.get("quantity_of_casesets")
        cases_per_caseset = options.get("cases_per_caseset")

        casesets_validator = quantity_range(
            MIN_CASESETS_QUANTITY, MAX_CASESETS_QUANTITY
        )
        try:
            casesets_validator(quantity_of_casesets)
        except ValidationError as exc:
            message = str(exc.detail[0])
            self.stdout.write(
                self.style.ERROR(
                    f"Error synthesizing case-sets. Got a ValidationError: {message}"
                )
            )
        else:
            cases_validator = quantity_range(
                MIN_CASES_QUANTITY, MAX_CASES_QUANTITY
            )
            try:
                cases_validator(cases_per_caseset)
            except ValidationError as exc:
                message = str(exc.detail[0])
                self.stdout.write(
                    self.style.ERROR(
                        f"Error synthesizing case sets. Got a ValidationError: {message}"
                    )
                )
            else:
                try:
                    case_sets = generate_casesets(
                        quantity_of_casesets, cases_per_caseset
                    )
                except SynthesisError as exc:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error synthesizing case sets. Got: {str(exc)}"
                        )
                    )
                else:
                    case_sets_ids = {case_set.id.hex for case_set in case_sets}
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully synthesized the following "
                            f"case sets {', '.join(case_sets_ids)}"
                        )
                    )
