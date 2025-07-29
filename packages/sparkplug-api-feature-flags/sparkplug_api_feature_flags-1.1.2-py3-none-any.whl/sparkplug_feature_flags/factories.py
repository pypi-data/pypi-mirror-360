import factory
from apps.users.factories import UserFactory

from sparkplug_feature_flags.models import FeatureFlag, FlagAccess


class FeatureFlagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeatureFlag

    uuid = factory.Faker("bothify", text="??????")
    title = factory.Faker("word")
    creator = factory.SubFactory(UserFactory)


class FlagAccessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlagAccess

    user = factory.SubFactory(UserFactory)
    feature_flag = factory.SubFactory(FeatureFlagFactory)
