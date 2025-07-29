from django.test import TestCase

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.models import FeatureFlag
from sparkplug_feature_flags.queries import feature_flag_list


class TestFeatureFlagsList(TestCase):
    def test_feature_flag_list_returns_all_flags_ordered_by_created_desc(self):
        # Arrange
        flag1 = FeatureFlagFactory(created="2023-01-01")
        flag2 = FeatureFlagFactory(created="2023-02-01")
        flag3 = FeatureFlagFactory(created="2023-03-01")

        # Act
        result = feature_flag_list()

        # Assert
        assert result.count() == 3
        assert list(result) == [flag3, flag2, flag1]
        assert isinstance(result.first(), FeatureFlag)
