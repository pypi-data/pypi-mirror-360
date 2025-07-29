from enum import Enum


class FeatureFlagAction(str, Enum):
    DELETE = "entities/featureFlags/REMOTE_DELETE"
    INSERT = "entities/featureFlags/REMOTE_INSERT"
    UPDATE = "entities/featureFlags/REMOTE_UPDATE"
