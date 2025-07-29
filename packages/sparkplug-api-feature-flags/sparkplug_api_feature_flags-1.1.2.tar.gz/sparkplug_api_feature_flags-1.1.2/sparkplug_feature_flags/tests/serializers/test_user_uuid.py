from apps.users.factories import UserFactory
from django.test import TestCase

from sparkplug_feature_flags.serializers import UserUuidSerializer


class TestUserUuidSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_valid_user_uuid(self):
        data = {"user_uuid": self.user.uuid}
        serializer = UserUuidSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.user_uuid == self.user.uuid

    def test_invalid_user_uuid(self):
        data = {"user_uuid": "nonexistent-uuid"}
        serializer = UserUuidSerializer(data=data)
        assert not serializer.is_valid()
        assert "user_uuid" in serializer.errors
