from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import re
from db import db
from routes import router
from pymongo import ReturnDocument
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from uuid import uuid4
from schemas import User, ProjectCreate, TaskCreate

from jwt_handler import jwt_decode
from routes import router, oauth2_scheme
from datetime import datetime



load_dotenv()

client = OpenAI(api_key=os.getenv("my_api_key"))

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

date_format = "%Y-%m-%d"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    auth_token = jwt_decode(token)

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.find_one({"id": auth_token["user_id"]})
    user["_id"] = str(user["_id"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def find_project(projects, project_id):
    for project in projects:
       if project["project_id"] == project_id:
           return project
    return None

@app.get("/get_user_details")
async def get_db(user: User = Depends(get_current_user)):
    user = await db.find_one({ "email": user["email"] })
    user["_id"] = str(user["_id"])
    return { "username":user["username"], "email": user["email"] }

@app.get("/get_projects")
async def get_db(user: User = Depends(get_current_user)):
    user = await db.find_one({ "email": user["email"] })
    user["_id"] = str(user["_id"])
    return user["projects"]

@app.get("/get_project/{projectId}")
async def get_db(projectId: str, user: User = Depends(get_current_user)):
    user = await db.find_one({ "email": user["email"] })
    user["_id"] = str(user["_id"])
    project = find_project(user["projects"], projectId)
    return project

def generate_prompt(description, start_date, end_date, priority):

    prompt = f"""
    Hello, I need your help in generating a schedule for my project. Here is the description of the project: {description}. 
    I want it to start on {start_date} and end on {end_date}. The priority of the project is {priority}.
    Use uuid to create unique ideas for each task.
    Can you break the project into smaller tasks and schedule them on different days so that I can manage my project? 
    Ensure that the tasks look like this example:
    {{"task_id": "2c3dfad0-b763-42fa-940f-e1995b041950",
        "name": "Project Initialization",
        "description":
            "Set up the project using create-react-app or Vite and install necessary dependencies such as react-router-dom for routing, Firebase or other backend service for user authentication and data storage.",
        "finished": False,
        "date": "2024-04-24T00:00:00",
        "time": "7:30 - 9:30 AM",
        "tag": {{ "name": "Backend", "color": "bg-green-200" }}
    }}
    Ensure that the tasks are stored in an array and your response should only contain the array and no other text.
    """
    return prompt

def generate_tasks(prompt):
    response = client.chat.completions.create(
      model="gpt-4",  
      messages=[
          {"role": "system", "content": "You are a helpful assistant that aids in planning projects."},
          {"role":"user", "content":prompt}
      ]
    )
    return response.choices[0].message.content

def create_tasks(description, start_date, end_date, priority, ):
    prompt = generate_prompt(description, start_date, end_date, priority)
    data = generate_tasks(prompt)
    match = re.search(r"\[\s*{.*}\s*\]", data, re.DOTALL)
    if match:
        json_array_string = match.group(0)
        tasks = json.loads(json_array_string) 
        print(tasks)
        return tasks
    else:
        print("No JSON array found")
        
    return
 
def extract_tags(tasks):
    unique_tags = {}
    for task in tasks:
        tag = task.get("tag")
        if tag:
            tag_name = tag.get("name")
            if tag_name not in unique_tags:
                unique_tags[tag_name] = tag
    return list(unique_tags.values())




@app.post("/create_project")
async def create_project(project: ProjectCreate, user: User = Depends(get_current_user)):
    project_id = str(uuid4())

    tasks = create_tasks(project.description, project.start_date, project.end_date, project.priority)
    tags = extract_tags(tasks)
    new_project = { "project_id": project_id ,"name": project.name, "description": project.description, "priority": project.priority,"finish": False, "tasks": tasks,"tags": tags ,"date_start": project.start_date, "date_end": project.end_date}
   
    user_profile = await db.update_one(
            {"email": user["email"]},
            {"$push": {"projects": new_project}},
            return_document = ReturnDocument.AFTER
        )
    if not user_profile:
        raise HTTPException(status_code=404, detail="Project not found or no permission")

    return new_project


@app.put("/create_task/{project_id}")
async def create_task(task: TaskCreate, project_id: str, user: User = Depends(get_current_user)):
    task_id = str(uuid4())
    converted_date = datetime.strptime(task.date, date_format)
    new_task = {
        "task_id": task_id,
        "name": task.name,
        "description": task.description,
        "finished": False,
        "date": converted_date,
        "time": task.time,
        "tag": {"name": task.tag.name, "color": task.tag.color}
    }


    user_profile = await db.find_one_and_update(
        {"email": user['email'], "projects.project_id": project_id},
        {"$push": {"projects.$.tasks": new_task}},
        return_document = ReturnDocument.AFTER
    )

    print(user_profile)

    if not user_profile:
        raise HTTPException(status_code=404, detail="Project not found or no permission")

    return new_task



@app.delete("/delete_project/{project_id}")
async def delete_project(project_id: str, user: User = Depends(get_current_user)):
    result = await db.update_one({ "email": user["email"] }, { "$pull": { "projects": { "project_id": project_id } } })

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return { "message": "Project successfully deleted." }