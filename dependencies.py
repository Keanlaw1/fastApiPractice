from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

import repositories
from database import get_db
from security import read_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/")


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=401,
        detail="Требуется действующий токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = read_access_token(token)
    except InvalidTokenError as exc:
        raise credentials_error from exc

    user = repositories.get_users(session, user_id)
    if user is None or not user.hashed_password:
        raise credentials_error

    request.state.user_id = user.id
    return user
