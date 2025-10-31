# app/utils/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from passlib.context import CryptContext

from app.config.settings import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,  
)
from app.database.db import get_db
from app.models.user import User

# ===================== 密碼雜湊 =====================
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


# ===================== JWT 生成 =====================
def create_access_token(sub: str, expires_minutes: Optional[int] = None) -> str:

    if expires_minutes is None:
        try:
            expires_minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES)
        except Exception:
            expires_minutes = 60

    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


# ===================== 取得目前登入者 =====================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user: Optional[User] = None
    try:
        user = db.get(User, UUID(str(sub)))
    except Exception:
        user = None

    if user is None:
        try:
            user = db.get(User, int(str(sub)))
        except Exception:
            user = None

    if user is None and "@" in str(sub):
        user = db.query(User).filter(User.email == str(sub)).first()

    if user is None:
        raise cred_exc
    return user
