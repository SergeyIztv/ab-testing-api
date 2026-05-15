from django.db import transaction
from django.utils.timezone import now
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from experiments.models import Device, Experiment, assign_variant
from experiments.serializers import ExperimentOutputSerializer


class ExperimentsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        device_token = request.headers.get("Device-Token")
        if not device_token:
            return Response({"error": "Device-Token header is required"}, status=400)

        with transaction.atomic():
            device, created = Device.objects.select_for_update().get_or_create(
                token=device_token,
                defaults={"created_at": now()},
            )

            experiments = Experiment.objects.filter(
                is_active=True, created_at__lte=device.created_at
            ).prefetch_related("variants")

            results = []
            for exp in experiments:
                variant = assign_variant(device, exp)
                results.append({"key": exp.key, "value": variant.value})

        serializer = ExperimentOutputSerializer(results, many=True)
        return Response({"experiments": serializer.data})
