from django.urls import path

from experiments.views import ExperimentsView

urlpatterns = [
    path("experiments/", ExperimentsView.as_view(), name="experiments"),
]
