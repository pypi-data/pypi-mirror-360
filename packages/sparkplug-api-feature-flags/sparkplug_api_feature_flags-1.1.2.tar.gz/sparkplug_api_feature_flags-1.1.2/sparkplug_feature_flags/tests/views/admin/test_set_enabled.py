from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestSetEnabledView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(user=self.user)
        self.feature_flag = FeatureFlagFactory(enabled=False)
        self.url = reverse(
            "sparkplug_feature_flags_admin:set_enabled",
            kwargs={"uuid": self.feature_flag.uuid},
        )

    def test_set_enabled_true(self):
        response = self.client.patch(
            self.url,
            {"enabled": True},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["enabled"] is True
        self.feature_flag.refresh_from_db()
        assert self.feature_flag.enabled is True

    def test_set_enabled_false(self):
        self.feature_flag.enabled = True
        self.feature_flag.save()
        response = self.client.patch(
            self.url,
            {"enabled": False},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["enabled"] is False
        self.feature_flag.refresh_from_db()
        assert self.feature_flag.enabled is False

    def test_set_enabled_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            self.url,
            {"enabled": True},
            format="json",
        )
        assert response.status_code == 401

    def test_set_enabled_invalid_uuid(self):
        url = reverse(
            "sparkplug_feature_flags_admin:set_enabled",
            kwargs={"uuid": "nonexistent-uuid"},
        )
        response = self.client.patch(
            url,
            {"enabled": True},
            format="json",
        )
        assert response.status_code == 404

    def test_set_enabled_invalid_payload(self):
        response = self.client.patch(
            self.url,
            {"enabled": "not-a-bool"},
            format="json",
        )
        assert response.status_code == 400
        assert "enabled" in response.data
