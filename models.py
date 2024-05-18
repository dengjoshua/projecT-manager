from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    google_token = Column(String(255), nullable=True)
    auth_type = Column(String(20))
    gender = Column(String(10), nullable=True, default="")
    DOB = Column(DateTime, nullable=True, default=None)
    picture = Column(String(255), nullable=True, default="")
    
    projects = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", back_populates="assignee")


class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    finished = Column(Boolean, default=False)
    priority = Column(String(20))
    date_start = Column(DateTime, default=datetime.utcnow)
    date_end = Column(DateTime, nullable=True)
    
    owner_id = Column(String, ForeignKey('users.id'))
    owner = relationship("User", back_populates="projects")
    
    tasks = relationship("Task", back_populates="project")
    tags = relationship("Tag", back_populates="project")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    finished = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    project_id = Column(String, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tasks")
    
    tag_id = Column(String, ForeignKey('tags.id'))
    tag = relationship("Tag", back_populates="tasks")
    
    assignee_id = Column(String, ForeignKey('users.id'))
    assignee = relationship("User", back_populates="assigned_tasks")

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    color = Column(String(50), nullable=False)
    project_id = Column(String, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tags")
    tasks = relationship("Task", back_populates="tag")