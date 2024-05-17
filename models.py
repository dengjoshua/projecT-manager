from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    google_token = Column(String(255), nullable=True)
    auth_type = Column(String(20))
    gender = Column(String(10), nullable=True)
    DOB = Column(DateTime, nullable=True)
    image_url = Column(String(255), nullable=True)
    
    projects = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", back_populates="assignee")

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(50), nullable=False)
    
    tasks = relationship("Task", back_populates="tag")

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
    tag_id = Column(Integer, ForeignKey('tags.id'))
    tag = relationship("Tag")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    finished = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    project_id = Column(String, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tasks")
    
    tag_id = Column(Integer, ForeignKey('tags.id'))
    tag = relationship("Tag", back_populates="tasks")
    
    assignee_id = Column(String, ForeignKey('users.id'))
    assignee = relationship("User", back_populates="assigned_tasks")