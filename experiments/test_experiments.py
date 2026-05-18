import hashlib
from collections import Counter

import pytest
from django.utils.timezone import now

from experiments.models import Assignment, Device, Experiment, Variant


@pytest.mark.django_db
class TestExperimentsAPI:

    def test_requires_device_token(self, api_client, experiments_url):
        resp = api_client.get(experiments_url)
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_deterministic_assignment(self, api_client, experiments_url, seed_experiments):
        resp1 = api_client.get(experiments_url, HTTP_DEVICE_TOKEN="same-device")
        resp2 = api_client.get(experiments_url, HTTP_DEVICE_TOKEN="same-device")
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json() == resp2.json()

    def test_experiments_in_response(self, api_client, experiments_url, seed_experiments):
        resp = api_client.get(experiments_url, HTTP_DEVICE_TOKEN="unique-device")
        data = resp.json()
        assert "experiments" in data
        keys = {e["key"] for e in data["experiments"]}
        assert "button_color" in keys
        assert "price" in keys

    def test_new_experiment_not_served_to_old_devices(self, api_client, experiments_url, seed_experiments):
        device = Device.objects.create(token="old-device", created_at=now())
        exp = Experiment.objects.create(
            key="new-exp", name="New", created_at=now()
        )
        resp = api_client.get(experiments_url, HTTP_DEVICE_TOKEN="old-device")
        keys = {e["key"] for e in resp.json()["experiments"]}
        assert "new-exp" not in keys

    def test_new_experiment_served_to_new_devices(self, api_client, experiments_url, seed_experiments):
        exp = Experiment.objects.create(
            key="new-exp-2", name="New 2", is_active=True, created_at=now()
        )
        Variant.objects.create(experiment=exp, value="A", weight=1000)
        resp = api_client.get(experiments_url, HTTP_DEVICE_TOKEN="brand-new-device")
        keys = {e["key"] for e in resp.json()["experiments"]}
        assert "new-exp-2" in keys

    def test_distribution_approximate(self, seed_experiments):
        exp = Experiment.objects.get(key="button_color")
        variants = list(exp.variants.all())
        total_weight = sum(v.weight for v in variants)

        n = 30000
        results = Counter()
        for i in range(n):
            hash_input = f"token-{i}:{exp.key}"
            hash_int = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
            bucket = hash_int % total_weight

            cumulative = 0
            for v in variants:
                cumulative += v.weight
                if bucket < cumulative:
                    results[v.value] += 1
                    break

        total = sum(results.values())
        for color, count in results.items():
            pct = count / total * 100
            assert pct == pytest.approx(33.3, abs=1)

    def test_assignment_stored_in_db(self, api_client, experiments_url, seed_experiments):
        api_client.get(experiments_url, HTTP_DEVICE_TOKEN="db-check-device")
        assert Assignment.objects.count() == 2

    def test_response_structure(self, api_client, experiments_url, seed_experiments):
        resp = api_client.get(experiments_url, HTTP_DEVICE_TOKEN="structure-check")
        data = resp.json()
        for exp in data["experiments"]:
            assert "key" in exp
            assert "value" in exp
