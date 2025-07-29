from django.test import TestCase
from sparkplug_core.serializers import SearchTermData

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.queries import feature_flag_autocomplete


class TestFeatureFlagAutocomplete(TestCase):
    def setUp(self):
        self.flag_a = FeatureFlagFactory(title="Alpha Feature")
        self.flag_b = FeatureFlagFactory(title="Beta Feature")
        self.flag_c = FeatureFlagFactory(title="Gamma Feature")
        self.flag_d = FeatureFlagFactory(title="Delta Feature")
        self.flag_e = FeatureFlagFactory(title="Epsilon Feature")

    def test_returns_all_flags_when_no_term(self):
        filters = SearchTermData(page=1, term="")
        results = list(feature_flag_autocomplete(filters))
        expected = {
            self.flag_a,
            self.flag_b,
            self.flag_c,
            self.flag_d,
            self.flag_e,
        }
        assert set(results) == expected

    def test_filters_by_term_case_insensitive(self):
        filters = SearchTermData(page=1, term="beta")
        results = list(feature_flag_autocomplete(filters))
        assert results == [self.flag_b]

    def test_orders_by_title(self):
        filters = SearchTermData(page=1, term="")
        results = list(feature_flag_autocomplete(filters))
        titles = [flag.title for flag in results]
        assert titles == sorted(titles)

    def test_pagination_first_page(self):
        filters = SearchTermData(page=1, term="")
        results = list(feature_flag_autocomplete(filters))
        all_flags = list(
            feature_flag_autocomplete(SearchTermData(page=1, term=""))
        )
        assert results == all_flags

    def test_no_results_for_non_matching_term(self):
        filters = SearchTermData(page=1, term="nonexistent")
        results = list(feature_flag_autocomplete(filters))
        assert results == []

    def test_partial_term_match(self):
        filters = SearchTermData(page=1, term="Fea")
        results = list(feature_flag_autocomplete(filters))
        titles = [flag.title for flag in results]
        assert all("fea" in title.lower() for title in titles)

    def test_empty_term_returns_all(self):
        filters = SearchTermData(page=1, term="")
        results = list(feature_flag_autocomplete(filters))
        assert len(results) == 5

    def test_none_term_returns_all(self):
        filters = SearchTermData(page=1, term=None)
        results = list(feature_flag_autocomplete(filters))
        assert len(results) == 5

    def test_invalid_page_defaults_to_first(self):
        filters = SearchTermData(page="notanint", term="")
        results = list(feature_flag_autocomplete(filters))
        expected = {
            self.flag_a,
            self.flag_b,
            self.flag_c,
            self.flag_d,
            self.flag_e,
        }
        assert set(results) == expected
