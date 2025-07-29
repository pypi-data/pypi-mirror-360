from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sparkplug_core.utils import (
    enforce_auth,
    get_paginated_response,
)

from ...queries import feature_flag_list
from ...serializers import FeatureFlagSerializer


class ListView(APIView):
    def get(self, request: Request) -> Response:
        enforce_auth("has_admin_access", request.user)

        return get_paginated_response(
            serializer_class=FeatureFlagSerializer,
            queryset=feature_flag_list(),
            request=request,
            view=self,
        )
