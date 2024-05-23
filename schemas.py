from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    finished: bool = False
    date: datetime = Field(default_factory=datetime.utcnow)
    tag_id: Optional[int] = None
    assignee_id: Optional[UUID] = None

    @validator("date", pre=True, always=True)
    def validate_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return datetime.fromisoformat(value)
        return value

class TaskCreate(TaskBase):
    tag_name: Optional[str] = None
    tag_color: Optional[str] = None

class TaskUpdate(TaskBase):
    name: Optional[str] = None
    description: Optional[str] = None
    finished: Optional[bool] = None
    date: Optional[str] = None

    @validator("date", pre=True, always=True)
    def validate_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return datetime.fromisoformat(value)
        return value

class Task(TaskBase):
    id: UUID
    project_id: UUID
    
    class Config:
        from_attributes = True

class TagCreate(BaseModel):
    name: str
    color: str

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    finished: bool = False
    priority: str
    date_start: datetime = Field(default_factory=datetime.utcnow)
    date_end: Optional[datetime] = None

    @validator("date_start", "date_end", pre=True, always=True)
    def validate_dates(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return datetime.fromisoformat(value)
        return value

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID
    owner_id: UUID
    tasks: List[Task] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: Optional[str] = None

class UserLogin(BaseModel):
    email:str
    password: str

class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[str] = None
    auth_type: Optional[str] = None
    gender: Optional[str] = None
    DOB: Optional[datetime] = None
    picture: Optional[str] = None

    @validator("DOB", pre=True, always=True)
    def validate_dob(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return datetime.fromisoformat(value)
        return value

class User(UserBase):
    id: str
    projects: List[Project] = []
    assigned_tasks: List[Task] = []

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    gender: Optional[str] = ""
    DOB: Optional[datetime] = None
    picture: Optional[str] = ""
    projects: List[int] = Field(default_factory=list)
    assigned_tasks: List[int] = Field(default_factory=list)

    class Config:
        from_attributes = True

class GoogleLoginData(BaseModel):
    token: str