from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sparkplug_core.serializers import SearchTermSerializer
from sparkplug_core.utils import (
    enforce_auth,
    get_validated_dataclass,
)

from ...queries import feature_flag_autocomplete
from ...serializers import FeatureFlagSerializer


class AutocompleteView(APIView):
    def get(self, request: Request) -> Response:
        enforce_auth("has_admin_access", request.user)

        filters = get_validated_dataclass(
            SearchTermSerializer,
            data={
                "term": request.query_params.get("term", ""),
                "page": request.query_params.get("page", 1),
            },
        )

        qs = feature_flag_autocomplete(filters)

        return Response(
            data=FeatureFlagSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )
