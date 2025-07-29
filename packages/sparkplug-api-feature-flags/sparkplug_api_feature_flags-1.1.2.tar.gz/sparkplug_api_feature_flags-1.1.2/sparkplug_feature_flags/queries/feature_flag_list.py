from django.db.models import QuerySet

from ..models import FeatureFlag


def feature_flag_list() -> QuerySet["FeatureFlag"]:
    return FeatureFlag.objects.all().order_by("-created")
