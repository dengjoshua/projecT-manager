from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
from typing import List
import os
from database import engine, get_db
from uuid import UUID
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routes.users import users_routes
from routes.projects import projects_routes
from routes.tasks import tasks_routes
from modal import App, asgi_app, Image, Secret

models.Base.metadata.create_all(bind=engine)


image = Image.debian_slim().pip_install_from_requirements("requirements.txt")

app = App("project-manager", image=image, secrets=[Secret.from_dotenv()])

web_app = FastAPI()

origins = ["*"]

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_app.include_router(users_routes)
web_app.include_router(projects_routes)
web_app.include_router(tasks_routes)


@app.function(image=image)
@asgi_app()
def fastapi_app():
    return web_app
