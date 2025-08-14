from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User
from schemas import SignupUser
from security import hash_password


def get_user_by_email(db: Session, email_id: str) -> Optional[User]:
    result = db.execute(select(User).where(User.email_id == email_id))
    return result.scalar_one_or_none()


def create_user(db: Session, user: SignupUser) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        full_name=user.full_name,
        email_id=user.email_id,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
