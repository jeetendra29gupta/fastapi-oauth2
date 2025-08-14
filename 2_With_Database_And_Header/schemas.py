from pydantic import BaseModel, EmailStr


class LoginUser(BaseModel):
    email_id: EmailStr
    password: str


class SignupUser(LoginUser):
    full_name: str
