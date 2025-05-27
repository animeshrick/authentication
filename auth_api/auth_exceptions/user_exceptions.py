import logging
from typing import Optional

from auth_api.auth_exceptions.base_exception import TheBaseException


class UserNotFoundError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "This user is not registered. Please register as new user."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class UserAlreadyVerifiedError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "This user is already verified."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class UserNotVerifiedError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "This user is not verified. Please verify your email first."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class EmailNotSentError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "Verification Email could not be sent."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class OTPNotVerifiedError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "OTP did not match."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class UserAuthenticationFailedError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "Password is invalid."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class UserNotAuthenticatedError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "The user is not authenticated, please re-login."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class PasswordNotMatchError(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "Password1 and Password2 do not match."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class NotValidUserID(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "User not found."
        else:
            super().__init__(msg)
        logging.error(self.msg)


class NotValidUserEmail(TheBaseException):
    def __init__(self, msg: Optional[str] = None):
        if not msg:
            self.msg = "Please provide a valid email."
        else:
            super().__init__(msg)
        logging.error(self.msg)
