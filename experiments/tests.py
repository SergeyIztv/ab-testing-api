import hashlib
from collections import Counter

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from experiments.models import (
    Assignment,
    Device,
    Experiment,
    Variant,
    assign_variant,
)


class ExperimentsAPITest(TestCase):
    def setUp(self):
        self.url = reverse("experiments")

    def test_requires_device_token(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.json())

    def test_deterministic_assignment(self):
        resp1 = self.client.get(self.url, HTTP_DEVICE_TOKEN="same-device")
        resp2 = self.client.get(self.url, HTTP_DEVICE_TOKEN="same-device")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp1.json(), resp2.json())

    def test_experiments_in_response(self):
        resp = self.client.get(self.url, HTTP_DEVICE_TOKEN="unique-device")
        data = resp.json()
        self.assertIn("experiments", data)
        keys = {e["key"] for e in data["experiments"]}
        self.assertIn("button_color", keys)
        self.assertIn("price", keys)

    def test_new_experiment_not_served_to_old_devices(self):
        device = Device.objects.create(token="old-device", created_at=now())
        # device created before experiment -> experiment not served
        exp = Experiment.objects.create(
            key="new-exp", name="New", created_at=now()
        )
        resp = self.client.get(self.url, HTTP_DEVICE_TOKEN="old-device")
        keys = {e["key"] for e in resp.json()["experiments"]}
        self.assertNotIn("new-exp", keys)

    def test_new_experiment_served_to_new_devices(self):
        exp = Experiment.objects.create(
            key="new-exp-2", name="New 2", is_active=True, created_at=now()
        )
        Variant.objects.create(experiment=exp, value="A", weight=1000)
        resp = self.client.get(self.url, HTTP_DEVICE_TOKEN="brand-new-device")
        keys = {e["key"] for e in resp.json()["experiments"]}
        self.assertIn("new-exp-2", keys)

    def test_distribution_approximate(self):
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
            self.assertAlmostEqual(pct, 33.3, delta=1)

    def test_assignment_stored_in_db(self):
        self.client.get(self.url, HTTP_DEVICE_TOKEN="db-check-device")
        self.assertEqual(Assignment.objects.count(), 2)

    def test_response_structure(self):
        resp = self.client.get(self.url, HTTP_DEVICE_TOKEN="structure-check")
        data = resp.json()
        for exp in data["experiments"]:
            self.assertIn("key", exp)
            self.assertIn("value", exp)
