# 🔐 FastAPI Authentication with JWT, Form and Local Database

A simple authentication and user profile management API built with **FastAPI**, using **JWT tokens
** for secure authentication.

---

## 🚀 Features

- JWT-based Authentication
- User registration (`/signup`)
- User login with JWT token generation (`/login`)
- Authenticated profile retrieval (`/profile`)
- Secure password hashing with bcrypt
- SQLite database integration with sqlalchemy
- Environment variable management with `.env`

---

## 🧪 API Endpoints

POST

```curl
curl -X 'POST' \
  'http://localhost:8181/signup/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email_id": "user@example.com",
  "password": "string",
  "full_name": "string"
}'
```

| Method | Endpoint   | Description             | Auth Required |
|--------|------------|-------------------------|---------------|
| POST   | `/signup`  | Register a new user     | ❌             |
| POST   | `/login`   | Login and get JWT token | ❌             |
| GET    | `/profile` | Get current user info   | ✅             |

---

## Screenshot

![img_0.png](img_0.png)
![img_1.png](img_1.png)
![img_2.png](img_2.png)
![img_3.png](img_3.png)
![img_4.png](img_4.png)
![img_5.png](img_5.png)
![img_6.png](img_6.png)
![img_7.png](img_7.png)


---

## logs

```text
(.venv) PS C:\Users\Admin\Workspace\fastapi-oauth2\1_With_Database_And_Form> python .\main.py
INFO:     Will watch for changes in these directories: ['C:\\Users\\Admin\\Workspace\\fastapi-oauth2\\1_With_Database_And_Form']
INFO:     Uvicorn running on http://0.0.0.0:8181 (Press CTRL+C to quit)
INFO:     Started reloader process [8248] using StatReload
INFO:     Started server process [18676]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:58861 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:58861 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:58865 - "POST /signup/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:58873 - "POST /login HTTP/1.1" 200 OK
INFO:     127.0.0.1:58874 - "GET /profile HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:58874 - "POST /login HTTP/1.1" 200 OK
INFO:     127.0.0.1:58874 - "GET /profile HTTP/1.1" 200 OK

```


