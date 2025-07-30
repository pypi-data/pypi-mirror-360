import base64
import secrets

from cryptography.fernet import Fernet
import string

from django.conf import settings


def generate_random_otp(int_length: int) -> str:
    random_otp = ''.join(secrets.choice(string.digits) for _ in range(int_length))
    return random_otp


def generate_key() -> bytes:
    secret_key = settings.SECRET_KEY.encode()
    key = base64.urlsafe_b64encode(secret_key[:32])
    return key


def encrypt_otp(otp: str) -> str:
    otp_bytes = otp.encode()
    fernet = Fernet(generate_key())

    encrypted_bytes = fernet.encrypt(otp_bytes)
    encrypted_otp = encrypted_bytes.decode()

    return encrypted_otp


def decrypt_otp(encrypted_otp) -> str:
    fernet = Fernet(generate_key())
    decrypted_otp = fernet.decrypt(encrypted_otp).decode()
    return decrypted_otp
