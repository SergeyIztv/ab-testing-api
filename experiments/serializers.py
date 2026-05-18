from rest_framework import serializers


class ExperimentOutputSerializer(serializers.Serializer):
    key = serializers.CharField(
        help_text='experiment name',
    )
    value = serializers.CharField(
        help_text='variant value',
    )

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField(
        help_text='error message',
    )

class ExperimentResponseSerializer(serializers.Serializer):
    experiments = ExperimentOutputSerializer(many=True)