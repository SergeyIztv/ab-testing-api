from django.db import models
from django.db.models import UniqueConstraint


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
        constraints = [
            UniqueConstraint(
                fields=["device", "experiment"],
                name="unique_device_experiment",
            )
        ]
