from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sparkplug_core.utils import enforce_auth

from ...models import FeatureFlag
from ...serializers import FeatureFlagSerializer


class DetailView(APIView):
    def get(self, request: Request, uuid: str) -> Response:
        enforce_auth("has_admin_access", request.user)

        instance = get_object_or_404(FeatureFlag, uuid=uuid)

        return Response(
            data=FeatureFlagSerializer(instance).data,
            status=status.HTTP_200_OK,
        )
