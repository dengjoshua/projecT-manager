from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from passlib.context import CryptContext
from uuid import uuid4
from fastapi.responses import JSONResponse
from jwt_handler import jwt_decode
from db import db  # Assuming db is your MongoDB connection
from schemas import UserLogin, UserCreate
from jwt_handler import sign_jwt

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth_token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    auth_token = jwt_decode(token)

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.find_one({"id": auth_token["user_id"]})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def verify_password(plain_password, hashed_password, user_id, email):
    if not pwd_context.verify(plain_password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return sign_jwt(user_id, email)

@router.post("/signup")
async def create_user(user: UserCreate):
    user_id = str(uuid4())

    if not await db.find_one({"email": user.email}):
        user_model = {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "hashed_password": pwd_context.hash(user.password),
            "projects": []
        }

        db.insert_one(user_model)

        return sign_jwt(user_id, user_model["email"])

    return HTTPException(status_code=500, detail="Email already in use.")

@router.post("/auth_token")
async def login(user: UserLogin):
    user_model = await db.find_one({"email": user.email})
    
    if not user_model:
        return HTTPException(status_code=400, detail="Incorrect email or password")
    return verify_password(user.password, user_model["hashed_password"], user_model["id"], user_model["email"])
