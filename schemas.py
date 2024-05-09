from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4
from datetime import datetime

class Tag(BaseModel):
    name: str
    color: str

class Task(BaseModel):
    name: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    finished: bool = False
    date: datetime = Field()
    tag: Optional[Tag] = None

class Project(BaseModel):
    name: str
    tasks: List[Task] = []
    project_id: str = Field(default_factory=lambda: str(uuid4()))
    finished: bool = False
    description: str
    priority: str
    date_start: datetime = Field()
    date_end: datetime = Field()
    tags: List[Tag] = []

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
    hashed_password: Optional[str] = None
    google_token: Optional[str] = None
    projects: List[Project] = []
    auth_type: str

class GoogleLoginData(BaseModel):
    token: str

class TaskCreate(BaseModel):
    name: str
    description: str
    date: str
    tag: Optional[Tag] = None


class ProjectCreate(BaseModel):
    name: str
    description: str
    priority: str
    start_date: str
    end_date: str

class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    end_date: Optional[datetime]
    finished: Optional[bool]

class ProjectDelete(BaseModel):
    project_id: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str