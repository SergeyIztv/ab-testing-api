import hashlib

from django.db import models


class Device(models.Model):
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class Experiment(models.Model):
    key = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("key",)


class Variant(models.Model):
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="variants"
    )
    value = models.CharField(max_length=255)
    weight = models.PositiveIntegerField(help_text="Weight out of 1000")

    class Meta:
        ordering = ("id",)
        unique_together = ("experiment", "value")


class Assignment(models.Model):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="assignments"
    )
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="assignments"
    )
    variant = models.ForeignKey(
        Variant, on_delete=models.CASCADE, related_name="assignments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("device", "experiment")


def assign_variant(device: Device, experiment: Experiment) -> Variant:
    existing = Assignment.objects.filter(
        device=device, experiment=experiment
    ).select_related("variant").first()
    if existing:
        return existing.variant

    total_weight = sum(
        experiment.variants.values_list("weight", flat=True)
    )
    hash_input = f"{device.token}:{experiment.key}"
    hash_int = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
    bucket = hash_int % total_weight

    cumulative = 0
    for variant in experiment.variants.all():
        cumulative += variant.weight
        if bucket < cumulative:
            Assignment.objects.create(
                device=device,
                experiment=experiment,
                variant=variant,
            )
            return variant

    last_variant = experiment.variants.last()
    Assignment.objects.create(
        device=device,
        experiment=experiment,
        variant=last_variant,
    )
    return last_variant
