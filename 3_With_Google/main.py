import jwt
import requests
from fastapi import FastAPI, Request, HTTPException, status
from fastapi import Security
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import Config

app = FastAPI()
security = HTTPBearer()


@app.get("/")
def home():
    return {"message": "Welcome! Visit /login/google to log in with Google."}


@app.get("/login/google")
def login_google():
    """Redirect user to Google OAuth consent screen"""
    google_oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={Config.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={Config.GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(url=google_oauth_url)


@app.get("/auth/google/callback")
def auth_google_callback(request: Request):
    """Handles callback from Google with auth code"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=token_data)
    if not token_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    access_token = token_response.json().get("access_token")

    # Fetch user info
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if not user_info_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    user_info = user_info_response.json()

    # Create JWT token with user's Google info
    payload = {
        "sub": user_info["id"],
        "email": user_info["email"],
        "name": user_info["name"]
    }

    jwt_token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    return {
        "message": "Login successful",
        "token": jwt_token,
        "user": user_info
    }


@app.get("/profile")
def profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]

    try:
        current_user = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return {
            "message": f"Hello, {current_user['name']}! This is a protected endpoint.",
            "user": current_user
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/dashboard")
def dashboard(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        current_user = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return {
            "message": f"Hello, {current_user['name']}! This is a protected endpoint.",
            "user": current_user
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8181, reload=True)
