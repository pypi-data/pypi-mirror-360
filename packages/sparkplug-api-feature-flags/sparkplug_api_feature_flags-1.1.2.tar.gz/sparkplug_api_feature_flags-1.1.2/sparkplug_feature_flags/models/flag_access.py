from django.conf import settings
from django.db import models
from sparkplug_core.models import BaseModel


class FlagAccess(
    BaseModel,
):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flag_access",
    )

    feature_flag = models.ForeignKey(
        to="sparkplug_feature_flags.FeatureFlag",
        on_delete=models.CASCADE,
        related_name="+",
    )

    def __str__(self) -> str:
        return f"{self.feature_flag.title} - {self.user.full_name}"
