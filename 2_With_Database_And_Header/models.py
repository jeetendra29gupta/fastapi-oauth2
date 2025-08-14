from sqlalchemy import Boolean, func, DateTime, Integer, String
from sqlalchemy.orm import mapped_column

from database import Base, engine


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = mapped_column(Integer, primary_key=True, index=True)
    full_name = mapped_column(String, index=True)
    email_id = mapped_column(String, unique=True, index=True)
    hashed_password = mapped_column(String)
    role = mapped_column(String, default='user')
    is_active = mapped_column(Boolean, default=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


def init_db() -> None:
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
