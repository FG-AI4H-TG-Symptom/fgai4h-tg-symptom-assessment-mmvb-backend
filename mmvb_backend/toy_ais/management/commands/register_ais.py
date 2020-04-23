from django.core.management.base import BaseCommand

from ais.models import AIImplementation
from toy_ais.implementations import TOY_AIS


class Command(BaseCommand):
    """Loads toy ai implementations into ai implementations"""

    def handle(self, *args, **options):
        for toy_ai in TOY_AIS:
            self.stdout.write(
                self.style.WARNING(
                    f"Tyring to register the following {toy_ai.name}..."
                )
            )

            try:
                AIImplementation.objects.get(name=toy_ai.name)
            except AIImplementation.DoesNotExist:
                # TODO: dynamically get server
                AIImplementation.objects.create(
                    name=toy_ai.name,
                    base_url=f"http://localhost:8000/toy_ais/{toy_ai.slug_name}",
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully registered {toy_ai.name}."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"{toy_ai.name} already registered, skipping."
                    )
                )
