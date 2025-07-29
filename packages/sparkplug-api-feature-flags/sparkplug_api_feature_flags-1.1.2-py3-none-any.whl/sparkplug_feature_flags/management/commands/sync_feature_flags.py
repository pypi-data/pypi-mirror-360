from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ...models import FeatureFlag

User = get_user_model()


class Command(BaseCommand):
    help = "Sync feature flags"
    params = None

    def handle(self, *args, **options: str) -> None:  # noqa: ARG002
        admin_user = User.objects.filter(is_staff=True, is_active=True).first()

        titles = [item["title"] for item in settings.FEATURE_FLAGS]

        FeatureFlag.objects.exclude(title__in=titles).delete()

        for item in settings.FEATURE_FLAGS:
            FeatureFlag.objects.get_or_create(
                title=item["title"],
                description=item["description"],
                enabled=True,
                creator=admin_user,
            )
