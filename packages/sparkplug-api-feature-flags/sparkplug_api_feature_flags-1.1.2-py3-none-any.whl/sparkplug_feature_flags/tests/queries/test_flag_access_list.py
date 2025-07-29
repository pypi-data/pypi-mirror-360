from apps.users.factories import UserFactory
from django.test import TestCase

from sparkplug_feature_flags.factories import FlagAccessFactory
from sparkplug_feature_flags.queries import flag_access_list


class TestFlagAccessList(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.flag_access = FlagAccessFactory(user=self.user)

    def test_flag_access_list(self):
        queryset = flag_access_list(
            self.user, self.flag_access.feature_flag.uuid
        )
        assert queryset.count() == 1
        assert queryset.first() == self.flag_access
