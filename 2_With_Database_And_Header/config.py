import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    required_envs = [JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, DATABASE_URL]
    if not all(required_envs):
        raise EnvironmentError("One or more required environment variables are missing.")
