from unittest.mock import patch

from apps.users.factories import UserFactory
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sparkplug_feature_flags.factories import FeatureFlagFactory


class TestSearchView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.url = reverse("sparkplug_feature_flags_admin:search")

    @patch("sparkplug_feature_flags.views.admin.search.feature_flag_search")
    def test_search_view_empty_results(self, mock_search):
        mock_search.return_value = []
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"term": "no-match", "page": 1})
        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
        assert response.data["results"] == []
        assert response.data["count"] == 0

    @patch("sparkplug_feature_flags.views.admin.search.feature_flag_search")
    def test_search_view_with_results(self, mock_search):
        feature_flag = FeatureFlagFactory(title="Test Feature Flag")
        mock_search.return_value = [feature_flag]
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"term": "Test", "page": 1})
        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == feature_flag.title

    def test_search_view_unauthenticated(self):
        response = self.client.get(self.url, {"term": "Test", "page": 1})
        assert response.status_code == 401
