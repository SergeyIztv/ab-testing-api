import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from experiments.models import Experiment, Variant


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def experiments_url():
    return reverse("experiments")


@pytest.fixture
def seed_experiments(db):
    button_color = Experiment.objects.create(
        key="button_color", name="Button Color"
    )
    Variant.objects.create(experiment=button_color, value="#FF0000", weight=333)
    Variant.objects.create(experiment=button_color, value="#00FF00", weight=333)
    Variant.objects.create(experiment=button_color, value="#0000FF", weight=334)

    price = Experiment.objects.create(key="price", name="Price")
    Variant.objects.create(experiment=price, value="10", weight=750)
    Variant.objects.create(experiment=price, value="20", weight=100)
    Variant.objects.create(experiment=price, value="50", weight=50)
    Variant.objects.create(experiment=price, value="5", weight=100)
