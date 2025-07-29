from dataclasses import dataclass

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_dataclasses.serializers import DataclassSerializer
from sparkplug_core.utils import (
    enforce_auth,
    get_validated_dataclass,
)
from sparkplug_core.views import WriteAPIView

from ...models import FeatureFlag
from ...serializers import FeatureFlagSerializer


@dataclass
class InputData:
    enabled: bool


class SetEnabledView(WriteAPIView):
    class InputSerializer(DataclassSerializer):
        class Meta:
            dataclass = InputData

    def patch(self, request: Request, uuid: str) -> Response:
        enforce_auth("has_admin_access", request.user)

        instance = get_object_or_404(FeatureFlag, uuid=uuid)

        validated_data: InputData = get_validated_dataclass(
            self.InputSerializer,
            data=request.data,
        )

        instance.enabled = validated_data.enabled
        instance.save()

        return Response(
            data=FeatureFlagSerializer(instance).data,
            status=status.HTTP_200_OK,
        )
