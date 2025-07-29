from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestListView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.url = reverse("sparkplug_feature_flags_admin:list")

        # Create some feature flags for testing
        FeatureFlagFactory.create_batch(3)

    def test_list_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
