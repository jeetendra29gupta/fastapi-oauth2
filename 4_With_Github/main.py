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
    return {"message": "Welcome! Visit /login/github to log in with GitHub."}


@app.get("/login/github")
def login_github():
    """Redirects to GitHub login"""
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={Config.GITHUB_CLIENT_ID}"
        f"&redirect_uri={Config.GITHUB_REDIRECT_URI}"
        "&scope=read:user user:email"
    )
    return RedirectResponse(url=github_auth_url)


@app.get("/auth/github/callback")
def github_callback(request: Request):
    """Handles GitHub OAuth callback"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    # Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        "client_id": Config.GITHUB_CLIENT_ID,
        "client_secret": Config.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": Config.GITHUB_REDIRECT_URI,
    }

    headers = {"Accept": "application/json"}
    token_response = requests.post(token_url, data=token_data, headers=headers)

    if not token_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    access_token = token_response.json().get("access_token")

    # Get user info from GitHub
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if not user_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    user = user_response.json()

    # Create JWT token
    payload = {
        "sub": str(user["id"]),
        "username": user["login"],
        "name": user.get("name"),
        "email": user.get("email"),
    }

    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    return {
        "message": "Login successful",
        "token": token,
        "user": user
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
