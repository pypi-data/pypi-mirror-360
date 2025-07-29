from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from sparkplug_core.utils import (
    enforce_auth,
    get_validated_dataclass,
)
from sparkplug_core.views import WriteAPIView

from ...models import FeatureFlag
from ...queries import flag_access_list
from ...serializers import (
    FeatureFlagSerializer,
    UserUuidData,
    UserUuidSerializer,
)


class RemoveAccessView(WriteAPIView):
    def patch(self, request: Request, uuid: str) -> Response:
        enforce_auth("has_admin_access", request.user)

        instance = get_object_or_404(FeatureFlag, uuid=uuid)

        validated_data: UserUuidData = get_validated_dataclass(
            UserUuidSerializer,
            data=request.data,
        )

        instance.users.remove(validated_data.user)

        qs = flag_access_list(request.user, uuid)

        return Response(
            data=FeatureFlagSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )
