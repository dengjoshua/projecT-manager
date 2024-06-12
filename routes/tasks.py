from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from models import User, Project, Tag, Task
import schemas
from sqlalchemy.orm import Session
from routes.users import get_current_user
from uuid import uuid4
from crud import organize_tasks, organize_project, organize_task, create_tag

tasks_routes = APIRouter()

@tasks_routes.get("/get_tasks/{project_id}")
def get_tasks(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    tasks_with_tags = organize_tasks(db=db, project_id=project_id)
    return tasks_with_tags

@tasks_routes.get("/assigned_tasks")
def get_assigned_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    tasks = db.query(Task).join(Task.assignees).filter(User.id == user.id).all()
    return tasks

@tasks_routes.post("/create_task/{project_id}")
def create_task(project_id: str, task: schemas.TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    task_id = str(uuid4())
    tag_id = create_tag(project_id=project_id, db=db, tag_name=task.tag_name, tag_color=task.tag_color)

    task_model = Task(
        id=task_id,
        name=task.name,
        date=task.date,
        description=task.description,
        project_id=project_id,
        finished=False,
        tag_id=tag_id
    )
    task_model.assignees.append(user)  # Assign the task to the user by default

    db.add(task_model)
    db.commit()
    return organize_task(task_id=task_id, db=db)

@tasks_routes.put("/edit_task/{task_id}")
def edit_task(task_id: str, task_update: schemas.TaskUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Not Authenticated.")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return organize_task(db=db, task_id=task_id)

@tasks_routes.post("/add_task_tag/{task_id}/{tag_id}")
def add_tag_to_task(tag_id: str, task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Unauthorized Access.")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")

    task.tag_id = tag_id
    db.commit()
    db.refresh(task)
    return task

@tasks_routes.get("/get_tags/{project_id}")
def get_tags(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Not Authenticated.")
    
    tags = db.query(Tag).filter(Tag.project_id == project_id).all()
    return tags

@tasks_routes.post("/create_tag/{task_id}")
def create_tag_for_task(tag: schemas.TagCreate, task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Not Authenticated.")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    tag_id = str(uuid4())
    tag_model = Tag(id=tag_id, name=tag.name, color=tag.color, project_id=task.project_id)
    db.add(tag_model)
    db.commit()
    return tag_model

@tasks_routes.delete("/delete_task/{task_id}")
def delete_task(task_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Not Authenticated.")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    db.delete(task)
    db.commit()

    project = organize_project(db=db, project_id=task.project_id)
    return project