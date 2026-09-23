import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    department = Column(String, nullable=True)
    priority = Column(String, default="Medium")
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    repository_url = Column(String, nullable=True)
    language = Column(String, default="Java")
    build_tool = Column(String, default="Maven")
    status = Column(String, default="Connected")
    created_at = Column(DateTime, default=datetime.utcnow)
    build_runs = relationship("BuildRun", back_populates="project", cascade="all, delete-orphan")


class BuildRun(Base):
    __tablename__ = "build_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    status = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    error_type = Column(String, nullable=True)
    raw_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="build_runs")
