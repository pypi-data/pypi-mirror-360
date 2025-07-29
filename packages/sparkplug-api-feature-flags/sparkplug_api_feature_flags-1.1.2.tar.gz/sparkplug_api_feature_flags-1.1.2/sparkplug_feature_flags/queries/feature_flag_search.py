from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import QuerySet
from sparkplug_core.serializers import SearchTermData

from .. import models


def feature_flag_search(
    filters: SearchTermData,
) -> QuerySet[models.FeatureFlag]:
    """Return a querySet filtered by trigram similarity on title."""
    qs = models.FeatureFlag.objects.all()
    if filters.term:
        qs = (
            qs.annotate(similarity=TrigramSimilarity("title", filters.term))
            .filter(similarity__gt=0.1)
            .order_by("-similarity")
        )
    return qs[filters.start : filters.end]
