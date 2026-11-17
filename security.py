import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummy-password-for-login-check")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30


def create_access_token(user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        os.environ["JWT_SECRET_KEY"],
        algorithm=JWT_ALGORITHM,
    )


def read_access_token(token):
    payload = jwt.decode(
        token,
        os.environ["JWT_SECRET_KEY"],
        algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "exp"]},
    )

    user_id = payload["sub"]
    if not isinstance(user_id, str) or not user_id.isascii():
        raise jwt.InvalidTokenError("Некорректный ID пользователя")
    if not user_id.isdecimal() or int(user_id) < 1:
        raise jwt.InvalidTokenError("Некорректный ID пользователя")

    return int(user_id)
