from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="NexusOps AI",
    description="Intelligent Business Workflow Automation Platform",
    version="1.0.0"
)

# Allow the React frontend to communicate with FastAPI
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
# TEMPORARY DATABASE
# -----------------------------

tasks = []


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
def get_tasks():

    return tasks


# -----------------------------
# CREATE TASK
# -----------------------------

@app.post("/tasks")
def create_task(task: TaskCreate):

    department = classify_task(task.description)

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "department": department,
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    tasks.append(new_task)

    return {
        "message": "Task created successfully",
        "task": new_task
    }


# -----------------------------
# UPDATE TASK
# -----------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):

    for item in tasks:

        if item["id"] == task_id:

            item["status"] = task.status

            return {
                "message": "Task updated successfully",
                "task": item
            }

    return {
        "message": "Task not found"
    }