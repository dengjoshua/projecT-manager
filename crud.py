from sqlalchemy.orm import Session
from models import User, Project, Tag, Task
from uuid import uuid4
import schemas

def get_tags(project_id: str, db: Session):
    return db.query(Tag).filter(Tag.project_id == project_id).all()

def create_tag(project_id: str, tag_name: str, tag_color: str, db: Session):
    tag_id = str(uuid4())
    tag_model = Tag(id=tag_id, name=tag_name, color=tag_color, project_id=project_id)
    db.add(tag_model)
    db.commit()
    return tag_id

def organize_task(task_id: str, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()
    tag = task.tag 
    assignees = task.assignees
    task_data = {
        'id': task.id,
        'project_id': task.project_id,
        'name': task.name,
        'description': task.description,
        'date': task.date,
        'finished': task.finished,
        'assignees': [{'id': assignee.id, 'name': assignee.name} for assignee in assignees],
        'tag': {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color
        } if tag else None
    }
    return task_data

def organize_tasks(project_id: str, db: Session):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    tasks_with_data = []

    for task in tasks:
        tag = task.tag 
        assignees = task.assignees
        task_data = {
            'id': task.id,
            'project_id': task.project_id,
            'name': task.name,
            'description': task.description,
            'date': task.date,
            'finished': task.finished,
            'assignees': [{'id': assignee.id, 'name': assignee.name} for assignee in assignees],
            'tag': {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color
            } if tag else None
        }
        tasks_with_data.append(task_data)

    return tasks_with_data

def organize_project(project_id: str, db: Session):
    project = db.query(Project).filter(Project.id == project_id).first()
    owner = project.owner
    assignees = project.assignees
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'finished': project.finished,
        'priority': project.priority,
        'date_start': project.date_start,
        'date_end': project.date_end,
        'tasks': organize_tasks(db=db, project_id=project.id),
        'owner': {
            'id': owner.id,
            'name': owner.name
        } if owner else None,
        'assignees': [{'id': assignee.id, 'name': assignee.name} for assignee in assignees],
        'tags': get_tags(project_id=project.id, db=db)
    }
    return project_data

def organize_projects(owner_id: str, db: Session):
    projects = db.query(Project).filter(Project.owner_id == owner_id).all()
    projects_with_tasks = []

    for project in projects:
        owner = project.owner
        assignees = project.assignees

        project_data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'finished': project.finished,
            'priority': project.priority,
            'date_start': project.date_start,
            'date_end': project.date_end,
            'tasks': organize_tasks(db=db, project_id=project.id),
            'owner': {
                'id': owner.id,
                'name': owner.name
            } if owner else None,
            'assignees': [{'id': assignee.id, 'name': assignee.name} for assignee in assignees],
            'tags': get_tags(project_id=project.id, db=db)
        }
        projects_with_tasks.append(project_data)

    return projects_with_tasks