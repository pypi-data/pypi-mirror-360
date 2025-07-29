from rest_framework import serializers
from rest_framework.serializers import Serializer

from .feature_flag import FeatureFlagSerializer


class FlagAccessSerializer(Serializer):
    uuid = serializers.CharField()
    feature_flag_uuid = serializers.CharField(source="feature_flag.uuid")
    feature_flag = FeatureFlagSerializer()
    user_uuid = serializers.CharField(source="user.uuid")
