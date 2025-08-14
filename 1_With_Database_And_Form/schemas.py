from pydantic import BaseModel, EmailStr


class SignupUser(BaseModel):
    email_id: EmailStr
    password: str
    full_name: str
