from django.urls import path
from toy_ais.views import ToyAIsView

urlpatterns = [
    path('<ai_slug_name>/<operation>', ToyAIsView.as_view()),
]
