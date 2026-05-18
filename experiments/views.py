from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from experiments.services import get_experiment_result
from experiments.serializers import ExperimentOutputSerializer, ErrorSerializer, ExperimentResponseSerializer
from logging import getLogger
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

logger = getLogger(__name__)

class ExperimentsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Get active experiments for a device",
        description="Returns active experiments with deterministically assigned variants "
                    "for the given device token. Same device always gets the same variant.",
        parameters=[
            OpenApiParameter(
                name="Device-Token",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Unique device identifier",
            ),
        ],
        responses={
            200: ExperimentResponseSerializer,
            400: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                name="Successful response",
                value={
                    "experiments": [
                        {
                            "key": "button_color",
                            "value": "FF0000",
                        },
                        {
                            "key": "price",
                            "value": "10",
                        }
                    ]
                },
                response_only=True,
                status_codes=[200],
            ),
        ]
    )
    def get(self, request: Request) -> Response:
        device_token = request.headers.get("Device-Token")
        if not device_token:
            logger.warning("Device-Token header is required")
            return Response({"error": "Device-Token header is required"}, status=400)

        results = get_experiment_result(device_token)

        serializer = ExperimentOutputSerializer(results, many=True)
        return Response({"experiments": serializer.data})
