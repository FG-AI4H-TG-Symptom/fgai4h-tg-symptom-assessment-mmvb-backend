from rest_framework import routers


class DefaultRouter(routers.DefaultRouter):
    """Custom Default Router that allows extending router registries"""

    def extend(self, router):
        """
        Extend the routes with url routes of the passed in router.

        Args:
             router: Router instance containing route definitions.
        """
        self.registry.extend(router.registry)
