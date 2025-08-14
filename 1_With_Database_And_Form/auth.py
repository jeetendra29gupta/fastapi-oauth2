from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from config import Config
from helper import get_user_by_email
from models import User
from security import verify_password


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user.email_id, "exp": expire}
    return jwt.encode(data, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        email_id = payload.get("sub")
        if not email_id:
            raise ValueError()
        return email_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_user(db: Session, email_id: EmailStr, password: str) -> User:
    user = get_user_by_email(db, email_id=email_id)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return user
