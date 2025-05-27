from auth_api.auth_exceptions.user_exceptions import UserNotVerifiedError, UserAuthenticationFailedError, \
    UserNotFoundError
from auth_api.export_types.request_data_types.login_user import LoginRequestType
from auth_api.models.user_models.abstract_user import AbstractUser
from auth_api.services.encryption_services.encryption_service import EncryptionServices


class User(AbstractUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @staticmethod
    def authenticate_user(request_data: LoginRequestType) -> bool:
        if request_data.email and request_data.password:
            user_exists = (
                True
                if User.objects.filter(email=request_data.email).count() > 0
                else False
            )
            if user_exists:

                user = User.objects.get(email=request_data.email)
                if user:
                    if (
                            EncryptionServices().decrypt(user.password)
                            == request_data.password
                    ):
                        if user.is_active and not user.is_deleted:
                            return True
                        else:
                            raise UserNotVerifiedError()
                    else:
                        raise UserAuthenticationFailedError()
                else:
                    raise UserNotFoundError()
            else:
                raise UserNotFoundError()
        else:
            raise ValueError("Provided Email or Password is invalid.")
