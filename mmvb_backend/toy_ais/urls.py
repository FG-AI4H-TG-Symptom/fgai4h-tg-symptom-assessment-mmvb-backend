from django.urls import path
from toy_ais.views import ToyAIsView

# defines url pattern for toy ai operation request
urlpatterns = [
    path("<ai_slug_name>/<operation>", ToyAIsView.as_view()),
]
