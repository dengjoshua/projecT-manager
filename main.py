from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
from typing import List
from database import engine, get_db
from uuid import UUID
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routes.users import users_routes
from routes.projects import projects_routes
from routes.tasks import tasks_routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_routes)
app.include_router(projects_routes)
app.include_router(tasks_routes)
