from fastapi import APIRouter, Depends, HTTPException
from routes.users import get_current_user
from models import User, Project
from database import get_db
from sqlalchemy.orm import Session
import schemas
from uuid import uuid4

projects_routes = APIRouter()

@projects_routes.get("/get_projects")
def get_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db) ):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    projects = db.query(Project).filter(Project.owner_id == user.id).all()

    return projects

@projects_routes.post("/create_project")
def create_project(project: schemas.ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials.")
    
    project_id = str(uuid4())

    db_project = Project(id=project_id, name=project.name, description=project.description, date_start=project.date_start, date_end=project.date_end, priority=project.priority, finished=False, owner_id = user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@projects_routes.delete("/delete_project/{project_id}")
def delete_project(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user credentials")
    
    project = db.query(Project).filter(Project.id == project_id).first()

    db.delete(project)
    db.commit()
    return { "message":"Successfully deleted the project." }