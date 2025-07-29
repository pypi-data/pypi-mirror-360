from rest_framework.serializers import SlugRelatedField

from ..models import FlagAccess


class FlagAccessUuidField(SlugRelatedField):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("queryset", FlagAccess.objects.all())
        kwargs.setdefault("slug_field", "uuid")
        kwargs.setdefault("source", "flag_access")
        super().__init__(**kwargs)
