from django.core.exceptions import ObjectDoesNotExist

from auth_api.auth_exceptions.user_exceptions import UserNotFoundError, PasswordNotMatchError
from auth_api.export_types.request_data_types.login_user import LoginRequestType
from auth_api.export_types.request_data_types.register_user import RegisterUserRequestType
from auth_api.export_types.request_data_types.update_password import UpdatePasswordRequestType
from auth_api.export_types.request_data_types.update_user_profile import UpdateUserProfileRequestType
from auth_api.export_types.user_types.export_user import ExportUser
from auth_api.models.user_models.user import User
from auth_api.serializers.forgor_password_serializer import ForgotPasswordSerializer
from auth_api.serializers.user_serializer import UserSerializer
from auth_api.services.encryption_services.encryption_service import EncryptionServices
from auth_api.services.helpers import validate_password_for_password_change, validate_phone, validate_dob, \
    validate_name, string_to_datetime, validate_address


class AuthServices:

    # @staticmethod
    # def logout_user(request) -> dict:
    #     refresh_token = request.headers.get("Authorization", "").split(" ")[1]
    #     if refresh_token:
    #         token = RefreshToken(refresh_token)
    #         token.payload["user_id"] = "1"
    #         token.blacklist()
    #     else:
    #         raise UserNotAuthenticatedError()
    #     return {"message": "User logged out successfully."}
    #
    # @staticmethod
    # def get_all_users_service() -> Optional[ExportUserList]:
    #     try:
    #         users = User.objects.all()
    #     except Exception:
    #         raise DatabaseError()
    #     if users:
    #         all_user_details = []
    #         for user in users:
    #             user_export_details = ExportUser(with_id=False, **user.model_to_dict())
    #             all_user_details.append(user_export_details)
    #         all_user_details = ExportUserList(user_list=all_user_details)
    #         return all_user_details
    #     else:
    #         return None
    #
    # @staticmethod
    # def get_searched_users(
    #     request_data: SearchUserRequestType, uid: str
    # ) -> Optional[list]:
    #     try:
    #         users = None
    #         keyword = request_data.keyword.strip()
    #         if validate_email_format(keyword):
    #             users = User.objects.filter(email=keyword, is_deleted=False)[:10]
    #         else:
    #             keywords = keyword.split(" ")
    #             query = Q()
    #             for keyword in keywords:
    #                 query |= Q(name__icontains=keyword)
    #
    #             query &= Q(is_deleted=False)
    #             users = User.objects.filter(query)[:10]
    #
    #         if users and users.exists():
    #             all_users = []
    #             for user in users:
    #                 if str(user.id) != uid:
    #                     user = ExportUser(**user.model_to_dict())
    #                     all_users.append(user)
    #
    #             if all_users and len(all_users) > 0:
    #                 return (
    #                     ExportUserList(user_list=all_users)
    #                     .model_dump()
    #                     .get("user_list")
    #                 )
    #         else:
    #             return None
    #
    #     except ObjectDoesNotExist:
    #         raise UserNotFoundError()

    @staticmethod
    def create_new_user_service(request_data: RegisterUserRequestType) -> dict:
        user: User = UserSerializer().create(data=request_data.model_dump())
        _user: User = User.objects.get(email=request_data.email, is_deleted=False, is_active=True)
        user_details = ExportUser(with_id=True, **_user.model_to_dict())
        if user:
            return {
                "data": user_details.model_dump(),
                "successMessage": "Registration done. You can login now.",
                "errorMessage": None,
            }

    @staticmethod
    def login(request_data: LoginRequestType) -> ExportUser | None:
        response = User.authenticate_user(request_data=request_data)
        user: User = User.objects.get(email=request_data.email, is_deleted=False, is_active=True)
        user_details = ExportUser(with_id=True, **user.model_to_dict())
        if response:
            return user_details.model_dump()
        else:
            raise UserNotFoundError()

    # def reset_password(self, email: str) -> dict:
    #     if validate_user_email(email=email).is_validated:
    #         reset_url = self.generate_reset_password_url(email=email)
    #         executor.submit(
    #             EmailServices.send_password_reset_email_by_user_email, email, reset_url
    #         )
    #         return {
    #             "successMessage": "Password reset email sent successfully.",
    #             "errorMessage": None,
    #         }
    #     else:
    #         raise UserNotFoundError()
    #
    # @staticmethod
    # def generate_reset_password_url(email: str) -> str:
    #     user = User.objects.get(email=email, is_deleted=False)
    #     token = (
    #         TokenGenerator()
    #         .get_tokens_for_user(ExportUser(**user.model_to_dict()))
    #         .get("access")
    #     )
    #     load_dotenv()
    #     FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL")
    #     reset_url = f"{FRONTEND_BASE_URL}/password-reset/{token}/"
    #     return reset_url
    #
    @staticmethod
    def change_password(request_data: UpdatePasswordRequestType):
        user_id: str = request_data.user_id
        user = User.objects.get(id=user_id, is_deleted=False)
        if request_data.password1 and request_data.password2:
            if validate_password_for_password_change(
                request_data.password1, request_data.password2
            ).is_validated:
                user.password = EncryptionServices().encrypt(request_data.password1)
                user.save()
            else:
                raise PasswordNotMatchError(
                    "Passwords are not matching or not in correct format."
                )
        else:
            raise ValueError("Please provide both the passwords.")

    @staticmethod
    def update_user_profile(
        uid: str, request_data: UpdateUserProfileRequestType
    ) -> ExportUser:
        user = User.objects.get(id=uid, is_deleted=False)
        if (
            request_data.image
            and isinstance(request_data.image, str)
            and request_data.image != ""
            and request_data.image != user.image
        ):
            user.image = request_data.image
        if (
            request_data.name
            and isinstance(request_data.name, str)
            and request_data.name != ""
            and request_data.name != user.name
        ):
            if validate_name(request_data.name).is_validated:
                user.name = request_data.name
            else:
                raise ValueError("Name is not in correct format.")
        if (
            request_data.dob
            and isinstance(request_data.dob, str)
            and request_data.dob != ""
            and request_data.dob != user.dob
        ):
            dob = string_to_datetime(request_data.dob)
            if validate_dob(dob).is_validated:
                user.dob = dob
            else:
                raise ValueError(validate_dob(dob).error)
        if (
            request_data.phone
            and isinstance(request_data.phone, str)
            and request_data.phone != ""
            and request_data.phone != user.phone
        ):
            if validate_phone(phone=request_data.phone).is_validated:
                user.phone = request_data.phone
            else:
                raise ValueError(validate_phone(phone=request_data.phone).error)
        if (
            request_data.address
            and isinstance(request_data.address, str)
            and request_data.address != ""
            and request_data.address != user.address
        ):
            if validate_address(address=request_data.address).is_validated:
                user.address = request_data.address
            else:
                raise ValueError(validate_address(address=request_data.address).error)
        user.save()
        return ExportUser(**user.model_to_dict())

    @staticmethod
    def get_user_details(uid: str) -> ExportUser:
        user = User.objects.get(id=uid, is_deleted=False, is_active=True)
        user_details = ExportUser(with_id=True, **user.model_to_dict())
        return user_details

    #
    @staticmethod
    def forgot_password_service(email: str, new_password: str) -> str:
        request: dict = {
            "email": email,
            "new_password": new_password,
        }
        resp_data: str = ForgotPasswordSerializer().retain_forgot_password(data=request)

        if resp_data:
            return resp_data
        else:
            raise UserNotFoundError()

    @staticmethod
    def get_user_details_by_id(requested_user_id: str, uid: str) -> ExportUser:
        try:
            requested_user = User.objects.get(id=requested_user_id, is_deleted=False, is_active=True)
            requested_user = ExportUser(**requested_user.model_to_dict())
            return requested_user
        except ObjectDoesNotExist:
            raise UserNotFoundError()

    # @staticmethod
    # def verify_user_with_otp(request_data: VerifyOTPRequestType):
    #     """
    #     Verify the user with the given OTP.
    #
    #     Args:
    #     - request_data (VerifyOTPRequestType): The object that contains the email and otp to verify.
    #
    #     Returns:
    #     - The token, if the user is verified.
    #
    #     Raises:
    #     - OTPNotVerifiedError: If the OTP is not verified.
    #     - UserAlreadyVerifiedError: If the user is already verified.
    #     - UserNotFoundError: If the user is not found.
    #     - ValueError: If the email and OTP are invalid.
    #     """
    #     email = request_data.email
    #     otp = request_data.otp
    #     if email and validate_user_email(email=email).is_validated:
    #         if otp and len(otp) == 6:
    #             user = User.objects.get(email=email, is_deleted=False)
    #             if not user.is_active:
    #                 response = OTPServices().verify_otp(user, otp)
    #                 if response:
    #                     token = TokenGenerator().get_tokens_for_user(user)
    #                     return token
    #                 else:
    #                     raise OTPNotVerifiedError()
    #             else:
    #                 raise UserAlreadyVerifiedError()
    #         else:
    #             raise OTPNotVerifiedError()
    #     else:
    #         raise UserNotFoundError()
