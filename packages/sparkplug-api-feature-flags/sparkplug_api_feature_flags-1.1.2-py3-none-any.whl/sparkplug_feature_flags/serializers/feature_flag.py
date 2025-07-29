from rest_framework import serializers


class FeatureFlagSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    created = serializers.DateTimeField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    enabled = serializers.BooleanField()
