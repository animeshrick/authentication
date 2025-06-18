import re
import uuid
from datetime import datetime
from dateutil.parser import parse

from django.core.exceptions import ObjectDoesNotExist

from auth_api.auth_exceptions.user_exceptions import UserNotFoundError
from auth_api.export_types.validation_types.validation_result import ValidationResult
from auth_api.models.user_models.user import User


def validate_email(email: str) -> ValidationResult:
    """
    This method is specifically to find if the email id is already registered with us or not. If registered it will return False, else True. This method is for validating email while creating new user.
    :param email: str
    :return: ValidationResult
    """
    if validate_email_format(email):
        existing_account = (
            True if User.objects.filter(email=email).count() > 0 else False
        )
        if existing_account:
            return ValidationResult(
                is_validated=False,
                error="An account with this email id is already existed.",
            )
        return ValidationResult(is_validated=True, error=None)
    else:
        return ValidationResult(is_validated=False, error="Email format is not correct")


def validate_user_email(email: str) -> ValidationResult:
    """
    This method is to check is the user email is a valid user or not. If registered it will return True, else False.
    :param email: str
    :return: ValidationResult
    """
    if validate_email_format(email):
        existing_account = (
            True if User.objects.filter(email=email).count() > 0 else False
        )
        if existing_account:
            return ValidationResult(
                is_validated=True,
                error=None,
            )
        return ValidationResult(is_validated=False, error="User does not exists.")
    else:
        return ValidationResult(is_validated=False, error="Email format is not correct")


def validate_user_uid(uid: str) -> ValidationResult:
    existing_account = True if User.objects.filter(id=uid).count() > 0 else False
    if existing_account:
        return ValidationResult(
            is_validated=True,
            error=None,
        )
    return ValidationResult(is_validated=False, error="User does not exists.")


def validate_recruiter(uid: str) -> ValidationResult:
    try:
        if validate_user_uid(uid).is_validated:
            if User.objects.get(id=uid).get_is_recruiter:
                return ValidationResult(is_validated=True, error=None)
            else:
                return ValidationResult(
                    is_validated=False, error="User is not a recruiter."
                )
        return ValidationResult(is_validated=False, error="User does not exists.")
    except ObjectDoesNotExist:
        raise UserNotFoundError()


def is_valid_uuid(value: str) -> bool:
    try:
        uuid_obj = uuid.UUID(value, version=4)
        return str(uuid_obj) == value
    except ValueError:
        return False


def validate_email_format(email: str) -> bool:
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def validate_name(name: str) -> ValidationResult:
    if name.lower().isalpha():
        return ValidationResult(is_validated=True, error=None)
    else:
        return ValidationResult(
            is_validated=False, error="First name or Last name can only have alphabets"
        )


def validate_role(role: str):
    """Validate that role is either 'seeker' or 'recruiter'"""
    if role.lower() not in ["seeker", "recruiter"]:
        raise ValidationResult(is_validated=True, error=None)
    return ValidationResult(
        is_validated=False, error="Invalid role. Allowed roles: seeker, recruiter."
    )


def validate_username(username: str) -> ValidationResult:
    """Checks if the received username matches the required conditions."""
    # Usernames can't be shorter than minlen
    if len(username) < 6:
        return ValidationResult(
            is_validated=False, error="Usernames can't be shorter than 6 characters"
        )
    # Usernames can only use letters, numbers, dots and underscores
    if not re.match("^[a-z0-9._]*$", username):
        return ValidationResult(
            is_validated=False,
            error="Usernames can only use letters, numbers, dots and underscores",
        )
    # Usernames can't begin with a number
    if username[0].isnumeric():
        return ValidationResult(
            is_validated=False, error="Usernames can't begin with a number"
        )
    return ValidationResult(is_validated=True, error=None)


def validate_password(password: str) -> ValidationResult:
    if len(password) >= 6:
        return ValidationResult(is_validated=True, error=None)
    return ValidationResult(
        is_validated=False, error="Password must be minimum of 6 characters"
    )


def validate_password_for_password_change(
        password1: str, password2: str
) -> ValidationResult:
    if password1 and password2:
        if len(password1) >= 6 and len(password2) >= 6:
            if password1 == password2:
                return ValidationResult(is_validated=True, error=None)
            else:
                return ValidationResult(
                    is_validated=False, error="Passwords do not match"
                )
        else:
            return ValidationResult(
                is_validated=False, error="Password must be minimum of 6 characters"
            )
    else:
        return ValidationResult(
            is_validated=False, error="Please provide both the passwords"
        )


def string_to_datetime(date_str: str) -> datetime:
    return parse(date_str)


def validate_dob(dob: datetime) -> ValidationResult:
    if calculate_age(dob) >= 13:
        return ValidationResult(is_validated=True, error=None)
    return ValidationResult(
        is_validated=False, error="Your age cannot be less than 13 years."
    )


def calculate_age(dob: datetime) -> int:
    try:
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None


def validate_phone(phone: str) -> ValidationResult:
    pattern = re.compile(r"^\+?[0-9]+\s?[0-9]*$")
    if pattern.match(phone):
        return ValidationResult(is_validated=True, error=None)
    else:
        return ValidationResult(
            is_validated=False, error="Phone number is not in valid format."
        )


def validate_address(address: str) -> ValidationResult:
    # Allows letters, numbers, commas, hyphens, periods, slashes, and spaces
    pattern = re.compile(r"^[\w\s.,#\-/]{5,100}$")
    if pattern.match(address):
        return ValidationResult(is_validated=True, error=None)
    else:
        return ValidationResult(
            is_validated=False, error="Address is not in valid format."
        )


def validate_pin(pincode: str) -> ValidationResult:
    if re.match(r"^\d{6}$", pincode):
        first_digit = int(pincode[0])
        if 1 <= first_digit <= 9:
            return ValidationResult(is_validated=True, error=None)
        else:
            return ValidationResult(
                is_validated=False,
                error="Invalid PIN code. The first digit should be between 1 and 9.",
            )
    else:
        print("Invalid PIN code. It should be a 6-digit number.")
        return ValidationResult(
            is_validated=False, error="Invalid PIN code. It should be a 6-digit number."
        )


def format_date(date: str) -> str:
    # Check if the string contains 'T' (indicating a time part)
    if "T" in date:
        # If it includes time, parse with time and timezone
        dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        # If it doesn't include time, parse only the date part
        dt = datetime.strptime(date, "%Y-%m-%d")

    # Format the datetime object to just the date part
    formatted_date = dt.strftime("%Y-%m-%d")

    print(formatted_date)
    return formatted_date
