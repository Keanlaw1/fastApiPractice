from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import settings

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummy-password-for-login-check")

JWT_ALGORITHM = "HS256"


def create_access_token(user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )


def read_access_token(token):
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "exp"]},
    )

    user_id = payload["sub"]
    if not isinstance(user_id, str) or not user_id.isascii():
        raise jwt.InvalidTokenError("Некорректный ID пользователя")
    if not user_id.isdecimal() or int(user_id) < 1:
        raise jwt.InvalidTokenError("Некорректный ID пользователя")

    return int(user_id)
