from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework_dataclasses.serializers import DataclassSerializer


@dataclass
class UserUuidData:
    user_uuid: str
    user: object = field(init=False, default=None)

    def __post_init__(self) -> None:
        """
        Load the user from the user_uuid field during initialization.
        """
        User = get_user_model()  # noqa: N806
        try:
            self.user = User.objects.get(uuid=self.user_uuid)
        except ObjectDoesNotExist as exc:
            raise ValidationError(
                detail={"user_uuid": ["User with this UUID does not exist."]}
            ) from exc


class UserUuidSerializer(DataclassSerializer):
    class Meta:
        dataclass = UserUuidData
        exclude = ("user",)  # Exclude the 'user' field from serialization
