import base64
import json


class BaseSessionBackend:
    def encode(self, session: dict) -> str:
        return base64.b64encode(json.dumps(session)).decode()

    def decode(self, data: str) -> dict:
        return json.loads(base64.b64decode(data.encode()))

