import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth import authenticate_user, create_access_token, decode_access_token
from database import get_db
from helper import get_user_by_email, create_user
from models import init_db
from schemas import SignupUser, LoginUser

load_dotenv()

app = FastAPI(title="FastAPI JWT Auth App")
security = HTTPBearer()


@app.post("/signup/", response_model=dict)
def signup(user: SignupUser, db: Session = Depends(get_db)) -> dict:
    """
    Register a new user.

    - **email_id**: User's email
    - **password**: Raw password
    - **full_name**: User's full name
    """
    if get_user_by_email(db, email_id=user.email_id):
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = create_user(db, user)

    return {
        "message": "User registered successfully.",
        "id": db_user.id,
        "full_name": db_user.full_name,
        "email": db_user.email_id,
        "role": db_user.role,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at.isoformat(),
        "updated_at": db_user.updated_at.isoformat() if db_user.updated_at else None,
    }


@app.post("/login", response_model=dict)
def login(user: LoginUser, db: Session = Depends(get_db)) -> dict:
    """
    Log in a user and return an access token.
    """
    user = authenticate_user(db, user.email_id, user.password)
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/profile", response_model=dict)
def profile(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> dict:
    """
    Get authenticated user's profile.
    """
    token = credentials.credentials
    email_id = decode_access_token(token)
    user = get_user_by_email(db, email_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User profile",
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email_id,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


@app.get('/dashboard', response_model=dict)
def dashboard(token: str = Header(..., alias="XToken"), db: Session = Depends(get_db)) -> dict:
    email_id = decode_access_token(token)
    user = get_user_by_email(db, email_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User profile",
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email_id,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


if __name__ == "__main__":
    init_db()
    # uvicorn main:app --host 0.0.0.0 --port 8181 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8181, reload=True)
