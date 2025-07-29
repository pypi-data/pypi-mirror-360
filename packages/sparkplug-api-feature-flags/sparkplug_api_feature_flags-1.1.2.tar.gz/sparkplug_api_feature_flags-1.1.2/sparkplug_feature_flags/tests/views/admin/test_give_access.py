from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestGiveAccessView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.feature_flag = FeatureFlagFactory()
        self.url = reverse(
            "sparkplug_feature_flags_admin:give_access",
            kwargs={"uuid": self.feature_flag.uuid},
        )

    def test_give_access(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.url,
            data={"user_uuid": self.user.uuid},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert "uuid" in response.data[0]
