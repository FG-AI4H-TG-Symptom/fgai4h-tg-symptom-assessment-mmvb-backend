from django.core.management.base import BaseCommand

from case_synthesizer.exceptions import SynthesisError
from case_synthesizer.generator import generate_cases


class Command(BaseCommand):
    """Generates synthetic cases"""

    def add_arguments(self, parser):
        parser.add_argument('quantity', type=int)

    def handle(self, *args, **options):
        quantity = options.get("quantity")
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
