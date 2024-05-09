import time
import jwt


JWT_SECRET = "1234"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {
        "auth_token": token,
        "token_type": "bearer",
        "status_code": 200
    }


def sign_jwt(user_id: str, email: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "expiry": time.time() + 30
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def jwt_decode(token: str):
    try:
        token_decode = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return token_decode

    except Exception as err:

        print(err)
        return None
