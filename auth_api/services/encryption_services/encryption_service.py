import base64
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv


class EncryptionServices:
    def encrypt(self, password: str):
        if not isinstance(password, str):
            raise ValueError(
                "Password not in string format. Unable to encrypt password."
            )
        load_dotenv()
        key = base64.b64encode(
            f"{os.environ.get('ENCRYPTION_PASSWORD'):<32}".encode("utf-8")
        )
        encryptor = Fernet(key=key)
        password = base64.b64encode(password.encode("utf-8"))
        encrypted_password = encryptor.encrypt(password)
        return encrypted_password

    def decrypt(self, encrypted_password: str) -> str:
        if not isinstance(encrypted_password, str):
            raise ValueError(
                "Password not in string format. Unable to encrypt password."
            )
        load_dotenv()
        key = base64.b64encode(
            f"{os.environ.get('ENCRYPTION_PASSWORD'):<32}".encode("utf-8")
        )
        encrypted_password = encrypted_password[2:-1].encode("utf-8")
        encryptor = Fernet(key=key)
        decrypted_password = encryptor.decrypt(encrypted_password)
        decrypted_password = base64.b64decode(decrypted_password).decode("utf-8")
        return decrypted_password
