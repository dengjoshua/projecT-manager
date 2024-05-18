from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from models import User, Project, Tag, Task
import schemas
from sqlalchemy.orm import Session
from routes.users import get_current_user
from uuid import uuid4

tasks_routes = APIRouter()

@tasks_routes.get("/get_tasks/{project_id}")
def get_tasks(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=501, detail="Invalid user credentials.")
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks

@tasks_routes.get("/assigned_tasks")
def get_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=501, detail="Invalid user credentials.")
    tasks = db.query(Task).filter(Task.assignee_id == user.id).all()
    return tasks

@tasks_routes.post("/create_task/{project_id}")
def create_tasks(project_id: str, task: schemas.TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=501, detail="Invalid user credentials.")
    
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    task_id = str(uuid4())


    task_model = Task(id=task_id, name=task.name, date=task.date, description=task.description, project_id=project_id, assignee_id=user.id, finished=False)

    db.add(task_model)
    db.commit()
    return task_model

@tasks_routes.get("/get_tags/{project_id}")
def get_tags(project_id: str, user: User= Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=501,detail="Not Authenticated.")
    
    tags = db.query(Tag).filter(Tag.project_id == project_id).all()
    return tags


@tasks_routes.post("/create_tag/{task_id}")
def create_tag(tag: schemas.TagCreate,task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=501, detail="Not Authenticated.")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    tag_id = str(uuid4())

    tag_model = Tag(id=tag_id, name=tag.name, color=tag.color, project_id=task.project_id)

    print(tag_model)

    db.add(tag_model)
    db.commit()
    return tag_model

@tasks_routes.delete("/delete_task/{task_id}")
def delete_task(task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=501, detail="Not Authenticated.")
    
    task = db.query(Task).filter(Task.id == task_id).first()

    db.delete(task)
    db.commit()

    return { "message":"Successfully deleted the task." }