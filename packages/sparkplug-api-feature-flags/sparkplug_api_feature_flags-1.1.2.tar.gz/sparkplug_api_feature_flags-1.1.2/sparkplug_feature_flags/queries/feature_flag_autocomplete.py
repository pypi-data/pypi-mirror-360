from django.db.models import QuerySet
from sparkplug_core.serializers import SearchTermData

from .. import models


def feature_flag_autocomplete(
    filters: SearchTermData,
) -> QuerySet[models.FeatureFlag]:
    qs = models.FeatureFlag.objects.all()
    if filters.term:
        qs = qs.filter(title__icontains=filters.term)
    return qs.order_by("title")[filters.start : filters.end]
