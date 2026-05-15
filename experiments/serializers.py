from rest_framework import serializers


class ExperimentOutputSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()
