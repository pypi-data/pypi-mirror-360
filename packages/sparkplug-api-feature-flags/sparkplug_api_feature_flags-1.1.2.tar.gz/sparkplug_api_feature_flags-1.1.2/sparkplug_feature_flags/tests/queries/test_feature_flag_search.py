from django.test import TestCase
from sparkplug_core.serializers import SearchTermData

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.models import FeatureFlag
from sparkplug_feature_flags.queries import feature_flag_search


class TestFeatureFlagSearch(TestCase):
    def setUp(self):
        self.flag1 = FeatureFlagFactory(title="Enable Dark Mode")
        self.flag2 = FeatureFlagFactory(title="Enable Light Mode")
        self.flag3 = FeatureFlagFactory(title="Experimental Feature")
        self.flag4 = FeatureFlagFactory(title="Beta Access")
        self.flag5 = FeatureFlagFactory(title="Dark Mode Beta")

    def test_returns_all_when_no_term(self):
        filters = SearchTermData(term=None, page=1)
        results = feature_flag_search(filters)
        assert set(results) == set(FeatureFlag.objects.all())

    def test_filters_by_trigram_similarity(self):
        filters = SearchTermData(term="dark", page=1)
        results = list(feature_flag_search(filters))
        titles = [flag.title for flag in results]
        assert "Enable Dark Mode" in titles
        assert "Dark Mode Beta" in titles
        assert "Enable Light Mode" not in titles

    def test_orders_by_similarity(self):
        filters = SearchTermData(term="dark mode", page=1)
        results = list(feature_flag_search(filters))
        assert results[0].title in ["Enable Dark Mode", "Dark Mode Beta"]

    def test_no_results_for_low_similarity(self):
        filters = SearchTermData(term="nonexistent", page=1)
        results = feature_flag_search(filters)
        assert list(results) == []
