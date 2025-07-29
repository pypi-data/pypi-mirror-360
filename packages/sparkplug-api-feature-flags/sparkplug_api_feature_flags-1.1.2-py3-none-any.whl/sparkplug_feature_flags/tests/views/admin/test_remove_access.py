from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestRemoveAccessView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.feature_flag = FeatureFlagFactory()
        self.url = reverse(
            "sparkplug_feature_flags_admin:remove_access",
            kwargs={"uuid": self.feature_flag.uuid},
        )

    def test_remove_access(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.url,
            data={"user_uuid": self.user.uuid},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 0
