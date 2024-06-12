from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from uuid import uuid4
from sqlalchemy.orm import Session
from jwt_handler import jwt_decode
import schemas
from jwt_handler import sign_jwt
from google_verify import verify_google_token
from models import User, Task, Project
from database import get_db
from dotenv import load_dotenv
import os
import smtplib
from fastapi.responses import JSONResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

users_routes = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth_token")

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

@users_routes.post("/send_email")
async def send_in_background(email: schemas.EmailSchema):
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = email.sender
        msg['To'] = email.receiver
        msg['Subject'] = email.subject

        plain_text = MIMEText(email.message, 'plain')
        html_text = MIMEText(f"<html><body>{email.message}</body></html>", 'html')

        msg.attach(plain_text)
        msg.attach(html_text)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email.sender, EMAIL_PASSWORD)
        server.sendmail(email.sender, email.receiver, msg.as_string())
        server.quit()

        print(f"Email sent to {email.receiver}")

    except Exception as e:
        print(f"Failed to send email: {e}")

    return JSONResponse(status_code=200, content={"message": "email has been sent"})

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    auth_token = jwt_decode(token)

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == auth_token["email"]).first()

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

@users_routes.post("/signup/normal")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_id = str(uuid4())

    check_user = db.query(User).filter(User.email == user.email).first() 

    if check_user:
        raise HTTPException(status_code=500, detail="Email already in use.") 

    db_user = User(id=user_id, name=user.name, email=user.email, hashed_password=pwd_context.hash(user.password), auth_type="normal")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return sign_jwt(user_id, user.email)


@users_routes.post("/signup/google")
def create_user(token: schemas.GoogleLoginData, db: Session = Depends(get_db)):

    user_info = verify_google_token(token.token)
    if user_info is None:
        raise HTTPException(status_code=401, detail="Invalid or expired Google token")
    
    existing_user = db.query(User).filter(User.email == user_info["email"]).first()
    if existing_user:
        return sign_jwt(existing_user.id, existing_user.email)

    user_id = str(uuid4())

    db_user = User(id=user_id, name=user_info['name'], email=user_info['email'], auth_type="google", picture=user_info['picture'])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return sign_jwt(user_id, user_info["email"])

@users_routes.post("/login/normal")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_model = db.query(User).filter(User.email == user.email).first()
    
    if not user_model:
        return HTTPException(status_code=400, detail="Incorrect email or password")
    return verify_password(user.password, user_model.hashed_password, user_model.id, user_model.email)

@users_routes.get("/users")
def get_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    users_with_projects = []

    for user in users:
        projects = []
        for project in user.assigned_projects:
            projects.append({
                'id': project.id,
                'name': project.name
            })

        tasks = []
        for task in user.assigned_tasks:
            tasks.append({
                'id': task.id,
                'name': task.name
            })

        user_data = {
            'name': user.name,
            'id': user.id,
            'email': user.email,
            'gender': user.gender,
            'DOB': user.DOB,
            'picture': user.picture,
            'projects': projects if projects else None,
            'tasks': tasks if tasks else None
        }
        users_with_projects.append(user_data)

    return users_with_projects

@users_routes.get("/user_details", response_model=schemas.UserResponse)
def get_user_details(user: User = Depends(get_current_user)):
    projects = [{'id': project.id, 'name': project.name} for project in user.assigned_projects]
    tasks = [{'id': task.id, 'name': task.name} for task in user.assigned_tasks]

    user_dict = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "gender": user.gender if user.gender is not None else "",
        "DOB": user.DOB.isoformat() if user.DOB else None,
        "picture": user.picture if user.picture is not None else "",
        "projects": projects,
        "tasks": tasks
    }
    return user_dict

@users_routes.put("/users/{user_id}")
def update_user(user_update: schemas.UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="User not found or no permission")
    
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    user_dict = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "gender": user.gender if user.gender is not None else "",
        "DOB": user.DOB.isoformat() if user.DOB else None,
        "picture": user.picture if user.picture is not None else "",
        "projects": [project.id for project in user.assigned_projects],
        "assigned_tasks": [task.id for task in user.assigned_tasks]
    }
    return user_dict