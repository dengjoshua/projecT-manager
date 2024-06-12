from fastapi import APIRouter, Depends, HTTPException
from routes.users import get_current_user
from models import User, Project, Tag, Task
from database import get_db
from sqlalchemy.orm import Session
import schemas
from uuid import uuid4
from crud import organize_project, organize_projects
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import re
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("my_api_key"))

projects_routes = APIRouter()

@projects_routes.get("/get_projects")
def get_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    projects = organize_projects(db=db, owner_id=user.id)

    return projects

@projects_routes.get("/get_project/{project_id}")
def get_project(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized Access.")
    
    project = db.query(Project).filter(Project.id == project_id).first()

    if project:
        return organize_project(db=db, project_id=project_id)

    raise HTTPException(status_code=404, detail="Project not found.")

@projects_routes.post("/create_project")
def create_project(project: schemas.ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    project_id = str(uuid4())

    db_project = Project(
        id=project_id,
        name=project.name,
        description=project.description,
        date_start=project.date_start,
        date_end=project.date_end,
        priority=project.priority,
        finished=False,
        owner_id=user.id
    )
    db_project.assignees.append(user)  # Assign the project to the creator by default
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def extract_tags(tasks):
    unique_tags = {}
    for task in tasks:
        tag = task.get("tag")
        if tag:
            name = tag.get("name")
            if name not in unique_tags:
                unique_tags[name] = tag
    return list(unique_tags.values())

def generate_prompt(description, start_date, end_date, priority, project_id, assignee_id):
    prompt = f"""
    Hello, I need your help in generating a schedule for my project. Here is the description of the project: {description}.
    I want it to start on {start_date} and end on {end_date}. The priority of the project is {priority}. The project_id is {project_id}, the assignee_id is {assignee_id}.
    Can you break the project into smaller tasks and schedule them on different days so that I can manage my project?
    Create tags based on the different parts of the project such as frontend, backend, debugging, etc.
    Generate placeholders that look like uuid4 ids and then add them to each tag id and task id.
    Ensure that the tasks look like this example:
    {{"id": "2c3dfad0-b763-42fa-940f-e1995b041950",
    "name": "Project Initialization",
    "tag_id":"2c3dfad0-b351-42fa-940f-e1995b0443d750",
    "tag":{{ "id":"2c3dfad0-b763-42fa-940f-e1995b0fsdu0", "name":"Frontend", "color":"bg-orange-400", "project_id":"38778-3ygsucsd-4838-asdsa" }},
    "project_id":"6dfa52ea-b763-42fa-36fa-e1355b346990",
    "assignee_id":"vjsndvs-3273ad-saf76asga-a872y8732g6",
    "description": "Set up the project using create-react-app or Vite and install necessary dependencies such as react-router-dom for routing, Firebase or other backend service for user authentication and data storage.",
    "finished": false,
    "date": "2024-04-24T00:00:00"}}
    Your response should contain only one array that contains the tasks.
    Make sure that the tag colors are of different types such as bg-slate-400.
    """
    return prompt

def generate_tasks(prompt):
    response = client.chat.completions.create(
      model="gpt-4",  
      messages=[
          {"role": "system", "content": "You are a helpful assistant that aids in planning projects."},
          {"role": "user", "content": prompt}
      ]
    )
    return response.choices[0].message.content

def create_tasks(description, start_date, end_date, priority, project_id, assignee_id, db: Session):
    prompt = generate_prompt(description, start_date, end_date, priority, project_id, assignee_id)
    data = generate_tasks(prompt)
    try:
        tasks_json_match = re.search(r'\[\s*{.*}\s*\]', data, re.DOTALL)

        if not tasks_json_match:
            return {"message": "Invalid response format"}

        tasks_json = tasks_json_match.group().strip()

        try:
            tasks = json.loads(tasks_json)
            tags = extract_tags(tasks)
            for tag_data in tags:
                tag = Tag(
                    id=tag_data["id"],
                    name=tag_data["name"],
                    color=tag_data["color"],
                    project_id=tag_data["project_id"]
                )
                db.add(tag)
            for task_data in tasks:
                task_date = datetime.fromisoformat(task_data["date"])
                task = Task(
                    id=task_data["id"],
                    name=task_data["name"],
                    tag_id=task_data["tag_id"],
                    project_id=task_data["project_id"],
                    assignee_id=task_data["assignee_id"],
                    description=task_data["description"],
                    finished=task_data["finished"],
                    date=task_date
                )
                db.add(task)
            db.commit()
            return
        
        except json.JSONDecodeError as e:
            return {'message': f"JSON decoding error: {e}"}

    except Exception as e:
        print(str(e))

@projects_routes.post("/create_project/ai")
async def create_project_ai(project: schemas.ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project_id = str(uuid4())

    db_project = Project(
        id=project_id,
        name=project.name,
        description=project.description,
        date_start=project.date_start,
        date_end=project.date_end,
        priority=project.priority,
        finished=False,
        owner_id=user.id
    )
    db_project.assignees.append(user)  # Assign the project to the creator by default
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    create_tasks(project.description, project.date_start, project.date_end, project.priority, project_id, user.id, db=db)

    organised_project = organize_projects(db=db, owner_id=user.id)
    return organised_project

@projects_routes.delete("/delete_project/{project_id}")
def delete_project(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    db.query(Task).filter(Task.project_id == project_id).delete(synchronize_session=False)
    db.query(Tag).filter(Tag.project_id == project_id).delete(synchronize_session=False)

    db.delete(project)
    db.commit()
    return {"message": "Successfully deleted the project."}