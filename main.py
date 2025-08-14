from urllib.parse import urlencode

import jwt
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

JWT_SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
JWT_ALGORITHM = "HS256"
GOOGLE_CLIENT_ID = "ABCDEFGHIJKLMNOPQRSTUVWXYZ.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GOOGLE_REDIRECT_URI = "http://localhost:8181/auth/google/callback"
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Google Oauth2</title>
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
        </head>
        <body>
            <div class="centered">
                <h2>Welcome to FastAPI Google OAuth2 Login</h2>
                <a href="/login/google">Login with Google</a>
            </div>
        </body>
    </html>
    """


@app.get("/login/google")
def login_google():
    """Redirect user to Google OAuth consent screen"""
    google_oauth_query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_oauth_url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(google_oauth_query_params)}"
    return RedirectResponse(url=google_oauth_url)


@app.get("/auth/google/callback")
def auth_google_callback(request: Request):
    """Handles callback from Google with auth code"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    # Exchange code for token
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(GOOGLE_TOKEN_ENDPOINT, data=token_data)
    if not token_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    # Fetch user info
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(GOOGLE_USERINFO_ENDPOINT, headers=headers)

    if not userinfo_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    userinfo = userinfo_response.json()

    # Create JWT token with user's Google info
    payload = {
        "sub": userinfo["id"],
        "email": userinfo["email"],
        "name": userinfo["name"]
    }

    jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    user_data = {
        "message": "Login successful",
        "token": jwt_token,
        "user": userinfo,
        "name": userinfo["name"],
        "email": userinfo["email"],
        "picture": userinfo["picture"]
    }
    return RedirectResponse(f"/profile?{urlencode(user_data)}")


@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    user_data = request.query_params

    name = user_data.get("name")
    email = user_data.get("email")
    picture = user_data.get("picture")

    return f"""
    <html>
        <head>
            <title>User Profile</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="centered">
                <h1>Welcome, {name}!</h1>
                <img src="{picture}" alt="Profile Picture" width="120"/><br>
                <p>Email: {email}</p>
                <a href="/logout/google" class="button">Logout</a>
            </div>
        </body>
    </html>
    """


@app.get("/logout/google", response_class=HTMLResponse)
def logout_google():
    return """
    <html>
        <head><title>Logged Out</title></head>
        <body style='text-align:center; font-family:sans-serif; margin-top: 20%;'>
            <h2>You have been logged out.</h2>
            <a href="/" style="text-decoration:none; color:#4285F4;">Go to Home</a>
        </body>
    </html>
    """


if __name__ == '__main__':
    import uvicorn

    # uvicorn main:app --host 0.0.0.0 --port 8181 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8181, reload=True)
