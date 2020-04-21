"""mmvb_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from rest_framework.schemas import get_schema_view

from ais.api.urls import router as ais_router
from cases.api.urls import router as cases_router
from common.routers import DefaultRouter
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

router = DefaultRouter(trailing_slash=False)
router.extend(ais_router)
router.extend(cases_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path(
        "openapi/",
        get_schema_view(
            title="WHO-ITU AI Benchmarking", description="", version="v1"
        ),
        name="openapi-schema",
    ),
    path(
        "api/docs/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
]

# TODO: try to do it in a cleaner way, using environment-dependant settings
if "toy_ais" in settings.INSTALLED_APPS:
    urlpatterns.append(
        path('toy_ais/', include('toy_ais.urls')),
    )
