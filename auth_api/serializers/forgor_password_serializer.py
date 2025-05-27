from typing import Optional

from rest_framework import serializers

from auth_api.auth_exceptions.user_exceptions import UserNotFoundError
from auth_api.export_types.validation_types.validation_result import ValidationResult
from auth_api.models.user_models.user import User
from auth_api.services.encryption_services.encryption_service import EncryptionServices
from auth_api.services.helpers import validate_password, validate_user_email


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def validate(self, data: Optional[dict] = None) -> Optional[bool]:
        email = data.get("email")
        new_password = data.get("new_password")

        # Email Validation
        if email and email != "" and isinstance(email, str):
            validation_result_email: ValidationResult = validate_user_email(email)
            is_validated_email = validation_result_email.is_validated
            if not is_validated_email:
                raise serializers.ValidationError(detail=validation_result_email.error)
            else:
                # Check if the email exists in the database
                existing_account = User.objects.filter(email=email, is_deleted=False, is_active=True).exists()
                if not existing_account:
                    raise UserNotFoundError()
        else:
            raise serializers.ValidationError(detail="Email should not be empty.")

        # Password Validation
        if new_password and new_password != "" and isinstance(new_password, str):
            validation_result_password: ValidationResult = validate_password(new_password)
            is_validated_password = validation_result_password.is_validated
            if not is_validated_password:
                raise serializers.ValidationError(validation_result_password.error)
        else:
            raise serializers.ValidationError(detail="New Password should not be empty.")

        return True

    def retain_forgot_password(self, data: dict) -> str | None:
        if self.validate(data):
            email = data.get("email")
            new_password = data.get("new_password")

            # Retrieve the user by email
            try:
                user = User.objects.get(email=email, is_deleted=False, is_active=True)
            except User.DoesNotExist:
                raise serializers.ValidationError(detail="User with the provided email does not exist.")

            # Encrypt and update the new password
            user.password = EncryptionServices().encrypt(new_password)
            user.save()

            if user:
                return "Password updated successfully."
