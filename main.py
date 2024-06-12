from fastapi import FastAPI
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from routes.users import users_routes
from routes.projects import projects_routes
from routes.tasks import tasks_routes
from modal import App, asgi_app, Image, Secret


Base.metadata.create_all(bind=engine)

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
