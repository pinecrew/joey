import datetime
import typing

from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

try:
    import jwt
    from cryptography.fernet import Fernet
except ImportError as e:
    print('PyJWT and cryptography are required. Install them or joey[sessions].')
    raise e


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: typing.Union[str, Secret],
        session_cookie: str = 'session',
        max_age: int = datetime.timedelta(weeks=2).total_seconds(),  # 14 days, in seconds
        same_site: str = 'lax',
        https_only: bool = False,
    ) -> None:
        self.app = app
        self.session_cookie = session_cookie
        self.secret_key = secret_key
        self.max_age = max_age
        self.security_flags = 'httponly; samesite=' + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += '; secure'

    def encode(self, session: dict) -> str:
        f = Fernet(self.secret_key)
        return f.encrypt(
            jwt.encode(
                {'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.max_age), **session},
                secret=self.secret_key,
                algorithms=['HS256'],
            ).encode()
        ).hex

    def decode(self, data: str) -> dict:
        try:
            f = Fernet(self.secret_key)
            data = f.decrypt(bytes.fromhex(data))
            return jwt.decode(data, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        session_data = connection.cookies.get(self.session_cookie, {})
        if session_data:
            session_data = self.decode(session_data)
            if session_data:
                initial_session_was_empty = False
        scope['session'] = session_data

        async def send_wrapper(message: Message) -> None:
            if message['type'] == 'http.response.start':
                if scope['session']:
                    # We have session data to persist.
                    headers = MutableHeaders(scope=message)
                    header_value = '%s=%s; path=/; Max-Age=%d; %s' % (
                        self.session_cookie,
                        self.encode(scope['session']),
                        self.max_age,
                        self.security_flags,
                    )
                    headers.append('Set-Cookie', header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = '%s=%s; %s' % (
                        self.session_cookie,
                        'null; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;',
                        self.security_flags,
                    )
                    headers.append('Set-Cookie', header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)
