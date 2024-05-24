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
from modal import App, asgi_app, Image, Secret

models.Base.metadata.create_all(bind=engine)

app = App("project-manager")
image = Image.debian_slim().pip_install_from_requirements("requirements.txt")

web_app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "https://project-manager-git-version14-deng-joshuas-projects.vercel.app/"
    "https://project-manager-git-version14-deng-joshuas-projects.vercel.app/"
]

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

@web_app.get("/home")
def test():
    return { "Testing the app." }

@app.function(image=image, secrets=[Secret.from_name("my-custom-secret")])
@asgi_app()
def fastapi_app():
    return web_app