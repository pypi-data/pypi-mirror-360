from rest_framework.serializers import SlugRelatedField

from ..models import FeatureFlag


class FeatureFlagUuidField(SlugRelatedField):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("queryset", FeatureFlag.objects.all())
        kwargs.setdefault("slug_field", "uuid")
        kwargs.setdefault("source", "feature_flag")
        super().__init__(**kwargs)
