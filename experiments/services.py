import hashlib

from django.db import transaction
from logging import getLogger
from experiments.models import Device, Experiment, Variant, Assignment

logger = getLogger(__name__)

def get_experiment_result(device_token: str) -> list[dict] | None:
    with transaction.atomic():
        device, created = Device.objects.select_for_update().get_or_create(
            token=device_token
        )

        experiments = Experiment.objects.filter(
            is_active=True, created_at__lte=device.created_at
        ).prefetch_related("variants")

        results = []
        for exp in experiments:
            try:
                variant = assign_variant(device, exp)
            except Exception as e:
                logger.exception(f"Failed to assign variant for experiment {exp.key}: {e}")
                continue

            results.append({"key": exp.key, "value": variant.value})

    logger.info(
        "Returned experiments for device_id: %d,\nresults: %s",
        device.id,
        results
    )

    return results

def assign_variant(device: Device, experiment: Experiment) -> Variant:
    existing = Assignment.objects.filter(
        device=device, experiment=experiment
    ).select_related("variant").first()
    if existing:
        return existing.variant

    variants_qs = experiment.variants.all()
    total_weight = sum(v.weight for v in variants_qs)
    hash_input = f"{device.token}:{experiment.key}"
    hash_int = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)

    if total_weight ==  0:
        logger.warning(f"Total weight is zero for experiment {experiment.key}")
        raise ZeroDivisionError("Total weight is zero")

    bucket = hash_int % total_weight

    cumulative = 0
    last_variant = None
    for variant in variants_qs:
        cumulative += variant.weight
        if bucket < cumulative:
            Assignment.objects.create(
                device=device,
                experiment=experiment,
                variant=variant,
            )
            return variant
        last_variant = variant
    Assignment.objects.create(
        device=device,
        experiment=experiment,
        variant=last_variant,
    )
    return last_variant