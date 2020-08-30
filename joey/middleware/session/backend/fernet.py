import datetime

from .base import BaseSessionBackend

try:
    import jwt
    from cryptography.fernet import Fernet
except ImportError as e:
    print('PyJWT and cryptography are required. Install them or joey[sessions].')
    raise e


class FernetSessionBackend(BaseSessionBackend):
    def __init__(self, cipher_key, signature_key=None, max_age=datetime.timedelta(weeks=2).total_seconds()):
        self.fernet = Fernet(cipher_key)
        self.signature_key = signature_key if signature_key else cipher_key
        self.max_age = max_age

    def encode(self, session: dict) -> str:
        return self.fernet.encrypt(
            jwt.encode(
                {'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.max_age), **session},
                self.signature_key,
                algorithm='HS256',
            ).encode()
        ).hex

    def decode(self, data: str) -> dict:
        try:
            data = self.fernet.decrypt(bytes.fromhex(data))
            return jwt.decode(data, self.signature_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {}
