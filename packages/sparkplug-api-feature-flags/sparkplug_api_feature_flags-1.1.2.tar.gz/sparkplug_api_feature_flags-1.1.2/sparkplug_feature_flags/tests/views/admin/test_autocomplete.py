from unittest.mock import patch

from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestAutocompleteView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.url = reverse("sparkplug_feature_flags_admin:autocomplete")

    @patch(
        "sparkplug_feature_flags.views.admin.autocomplete.feature_flag_autocomplete"
    )
    def test_autocomplete_view_success(self, mock_autocomplete):
        feature_flag = FeatureFlagFactory(title="Test Flag")
        mock_autocomplete.return_value = [feature_flag]
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"term": "Test", "page": 1})
        assert response.status_code == 200
        assert response.data
        first_item = response.data[0]
        assert first_item["title"] == feature_flag.title
        assert first_item["uuid"] == feature_flag.uuid

    @patch(
        "sparkplug_feature_flags.views.admin.autocomplete.feature_flag_autocomplete"
    )
    def test_autocomplete_view_empty_results(self, mock_autocomplete):
        mock_autocomplete.return_value = []
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"term": "unknown", "page": 1})
        assert response.status_code == 200
        assert response.data == []

    def test_autocomplete_view_unauthenticated(self):
        response = self.client.get(self.url, {"term": "Test", "page": 1})
        assert response.status_code == 401
