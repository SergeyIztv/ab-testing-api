from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from experiments.services import get_experiment_result
from experiments.serializers import ExperimentOutputSerializer
from logging import getLogger

logger = getLogger(__name__)

class ExperimentsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        device_token = request.headers.get("Device-Token")
        if not device_token:
            logger.warning("Device-Token header is required")
            return Response({"error": "Device-Token header is required"}, status=400)

        results = get_experiment_result(device_token)

        serializer = ExperimentOutputSerializer(results, many=True)
        return Response({"experiments": serializer.data})
