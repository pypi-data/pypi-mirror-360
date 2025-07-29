from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet

from ..models import FlagAccess


def flag_access_list(
    user: type[AbstractBaseUser],
    feature_flag_uuid: str,
) -> QuerySet["FlagAccess"]:
    return FlagAccess.objects.filter(
        user=user,
        feature_flag__uuid=feature_flag_uuid,
    )
