from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database import Base, engine, get_db, Task

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexusOps AI",
    description="Intelligent Business Workflow Automation Platform",
    version="2.0.0"
)

# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# DATA MODELS
# -----------------------------

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "Medium"


class TaskUpdate(BaseModel):
    status: str


# -----------------------------
# AI CLASSIFICATION
# -----------------------------

def classify_task(description: str):

    text = description.lower()

    if any(word in text for word in [
        "laptop",
        "computer",
        "wifi",
        "internet",
        "software",
        "password",
        "network",
        "printer"
    ]):
        return "IT"

    if any(word in text for word in [
        "salary",
        "leave",
        "employee",
        "hr",
        "attendance",
        "recruitment"
    ]):
        return "HR"

    if any(word in text for word in [
        "invoice",
        "payment",
        "budget",
        "expense",
        "finance"
    ]):
        return "Finance"

    if any(word in text for word in [
        "customer",
        "client",
        "sales",
        "order"
    ]):
        return "Sales"

    return "Operations"


# -----------------------------
# ROOT
# -----------------------------

@app.get("/")
def root():

    return {
        "message": "Welcome to NexusOps AI",
        "status": "running"
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# -----------------------------
# GET TASKS
# -----------------------------

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):

    tasks = db.query(Task).order_by(Task.id.desc()).all()

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "department": task.department,
            "status": task.status,
            "created_at": (
                task.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if task.created_at
                else None
            )
        }
        for task in tasks
    ]


# -----------------------------
# CREATE TASK
# -----------------------------

@app.post("/tasks")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):

    department = classify_task(task.description)

    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        department=department,
        status="Pending",
        created_at=datetime.now()
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "message": "Task created successfully",
        "task": {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "priority": new_task.priority,
            "department": new_task.department,
            "status": new_task.status,
            "created_at": new_task.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
    }


# -----------------------------
# UPDATE TASK
# -----------------------------

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db)
):

    item = db.query(Task).filter(Task.id == task_id).first()

    if not item:
        return {
            "message": "Task not found"
        }

    item.status = task.status

    db.commit()
    db.refresh(item)

    return {
        "message": "Task updated successfully",
        "task": {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "priority": item.priority,
            "department": item.department,
            "status": item.status,
            "created_at": (
                item.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if item.created_at
                else None
            )
        }
    }