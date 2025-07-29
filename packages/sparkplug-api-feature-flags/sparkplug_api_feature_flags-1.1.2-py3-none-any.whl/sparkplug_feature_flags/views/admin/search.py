from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sparkplug_core.serializers import SearchTermSerializer
from sparkplug_core.utils import (
    enforce_auth,
    get_paginated_response,
    get_validated_dataclass,
)

from ...queries import feature_flag_search
from ...serializers import FeatureFlagSerializer


class SearchView(APIView):
    def get(self, request: Request) -> Response:
        enforce_auth("has_admin_access", request.user)

        filters = get_validated_dataclass(
            SearchTermSerializer,
            data={
                "term": request.query_params.get("term", ""),
                "page": request.query_params.get("page", 1),
            },
        )

        return get_paginated_response(
            serializer_class=FeatureFlagSerializer,
            queryset=feature_flag_search(filters),
            request=request,
            view=self,
        )
