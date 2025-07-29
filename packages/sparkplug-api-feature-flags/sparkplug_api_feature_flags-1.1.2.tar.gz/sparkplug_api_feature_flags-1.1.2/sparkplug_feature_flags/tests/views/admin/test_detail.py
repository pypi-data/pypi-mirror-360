from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestDetailView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.non_staff_user = UserFactory(is_staff=False)
        self.feature_flag = FeatureFlagFactory()
        self.url = reverse(
            "sparkplug_feature_flags_admin:detail",
            kwargs={"uuid": self.feature_flag.uuid},
        )

    def test_get_detail_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data["uuid"] == str(self.feature_flag.uuid)
        assert response.data["title"] == self.feature_flag.title

    def test_get_detail_unauthenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_get_detail_forbidden_for_non_staff(self):
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_get_detail_not_found(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "sparkplug_feature_flags_admin:detail",
            kwargs={"uuid": "00000000-0000-0000-0000-000000000000"},
        )
        response = self.client.get(url)
        assert response.status_code == 404
