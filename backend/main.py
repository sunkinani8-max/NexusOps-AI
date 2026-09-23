import json
import re
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import Base, BuildRun, Project, Task, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexusOps AI",
    description="Intelligent DevOps and business workflow automation platform",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=2, max_length=2000)
    priority: str = "Medium"


class TaskUpdate(BaseModel):
    status: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    repository_url: str | None = None
    language: str = "Java"
    build_tool: str = "Maven"


class ProjectAnalyze(BaseModel):
    project_id: int
    files: list[str] = Field(default_factory=list)


class BuildAnalyze(BaseModel):
    project_id: int | None = None
    log_text: str = Field(min_length=5, max_length=30000)


class ExplainError(BaseModel):
    error_text: str = Field(min_length=3, max_length=10000)


# Existing business workflow classification

def classify_task(description: str):
    text = description.lower()
    if any(word in text for word in ["laptop", "computer", "wifi", "internet", "software", "password", "network", "printer"]):
        return "IT"
    if any(word in text for word in ["salary", "leave", "employee", "hr", "attendance", "recruitment"]):
        return "HR"
    if any(word in text for word in ["invoice", "payment", "budget", "expense", "finance"]):
        return "Finance"
    if any(word in text for word in ["customer", "client", "sales", "order"]):
        return "Sales"
    return "Operations"


# DevOps analysis helpers. These are deterministic today and provide a safe seam for a real LLM/RAG provider later.

def explain_error_text(error_text: str) -> dict:
    text = error_text.lower()
    if "could not resolve dependencies" in text or "dependencyresolutionexception" in text or "artifact" in text and "not found" in text:
        return {
            "error_type": "Dependency resolution",
            "root_cause": "Maven could not download or locate a required dependency.",
            "explanation": "The dependency version, repository configuration, network access, or local Maven cache may be incorrect.",
            "suggestions": [
                "Verify the groupId, artifactId, and version in pom.xml.",
                "Check the configured Maven repositories and network access.",
                "Run mvn -U clean verify to refresh dependency metadata.",
            ],
        }
    if "compilation failure" in text or "cannot find symbol" in text or "compilation error" in text:
        return {
            "error_type": "Compilation failure",
            "root_cause": "The Java compiler found an invalid reference or source-level error.",
            "explanation": "A class, method, import, or type may be missing, renamed, or incompatible with the configured Java version.",
            "suggestions": [
                "Read the first compiler error before investigating later cascading errors.",
                "Check imports, method signatures, and package names.",
                "Confirm the Maven compiler source and target versions.",
            ],
        }
    if "test failures" in text or "failures:" in text or "assertionerror" in text or "there are test failures" in text:
        return {
            "error_type": "Test failure",
            "root_cause": "One or more automated tests did not produce the expected result.",
            "explanation": "The application behavior, test data, environment, or assertion may no longer match the intended requirement.",
            "suggestions": [
                "Open the surefire report for the first failing test.",
                "Re-run the specific test with Maven debug output.",
                "Check recent code or fixture changes before changing the assertion.",
            ],
        }
    if "permission denied" in text or "accessdenied" in text or "401" in text or "403" in text:
        return {
            "error_type": "Access or permission issue",
            "root_cause": "The build or integration request was rejected because credentials or permissions are insufficient.",
            "explanation": "The configured token, repository permissions, or service account may be missing, expired, or scoped incorrectly.",
            "suggestions": [
                "Check the active credentials without committing secrets to the repository.",
                "Confirm the account has access to the repository or package registry.",
                "Review CI/CD secret names and environment variables.",
            ],
        }
    return {
        "error_type": "Unclassified build or runtime issue",
        "root_cause": "The supplied log does not match a known NexusOps pattern yet.",
        "explanation": "Capture the first error block and its surrounding context so the analyzer can narrow down the cause.",
        "suggestions": [
            "Share the first error and the command that produced it.",
            "Check the full stack trace and the earliest failing module.",
            "Re-run with Maven -e or -X when deeper diagnostics are required.",
        ],
    }


def analyze_project_files(files: list[str]) -> dict:
    normalized = [file.replace("\\", "/") for file in files]
    lower = [file.lower() for file in normalized]
    has_pom = any(file.endswith("pom.xml") for file in lower)
    has_gradle = any(file.endswith("build.gradle") or file.endswith("build.gradle.kts") for file in lower)
    has_java = any("src/main/java/" in file or file.endswith(".java") for file in lower)
    has_tests = any("src/test/" in file or "/test/" in file for file in lower)
    has_docker = any(file.endswith("dockerfile") or "/dockerfile" in file for file in lower)
    has_ci = any(".github/workflows/" in file or ".gitlab-ci" in file or "jenkinsfile" in file for file in lower)
    detected = []
    if has_pom:
        detected.append("Maven project descriptor")
    if has_gradle:
        detected.append("Gradle build descriptor")
    if has_java:
        detected.append("Java source")
    if has_tests:
        detected.append("Automated tests")
    if has_docker:
        detected.append("Container definition")
    if has_ci:
        detected.append("CI/CD workflow")
    score = min(100, 30 + len(detected) * 12)
    return {
        "file_count": len(normalized),
        "detected_components": detected,
        "signals": {
            "maven": has_pom,
            "gradle": has_gradle,
            "java": has_java,
            "tests": has_tests,
            "docker": has_docker,
            "ci_cd": has_ci,
        },
        "readiness_score": score,
        "recommendations": [
            "Add a pom.xml file." if not has_pom and not has_gradle else "Keep build metadata versioned with the project.",
            "Add tests under src/test/ to make build health measurable." if not has_tests else "Keep test failures visible in the build dashboard.",
            "Add a CI/CD workflow for repeatable validation." if not has_ci else "Document the CI/CD workflow and required secrets.",
        ],
    }


def project_dict(project: Project) -> dict:
    return {
        "id": project.id,
        "name": project.name,
        "repository_url": project.repository_url,
        "language": project.language,
        "build_tool": project.build_tool,
        "status": project.status,
        "created_at": project.created_at.strftime("%Y-%m-%d %H:%M:%S") if project.created_at else None,
    }


def build_dict(run: BuildRun) -> dict:
    return {
        "id": run.id,
        "project_id": run.project_id,
        "status": run.status,
        "summary": run.summary,
        "error_type": run.error_type,
        "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S") if run.created_at else None,
    }


@app.get("/")
def root():
    return {"message": "Welcome to NexusOps AI", "status": "running", "version": app.version}


@app.get("/health")
def health():
    return {"status": "healthy"}


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
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else None,
        }
        for task in tasks
    ]


@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    allowed_priorities = {"Low", "Medium", "High", "Critical"}
    if task.priority not in allowed_priorities:
        raise HTTPException(status_code=422, detail=f"Priority must be one of: {', '.join(sorted(allowed_priorities))}")
    new_task = Task(
        title=task.title.strip(),
        description=task.description.strip(),
        priority=task.priority,
        department=classify_task(task.description),
        status="Pending",
        created_at=datetime.utcnow(),
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task created successfully", "task": {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "priority": new_task.priority,
        "department": new_task.department,
        "status": new_task.status,
        "created_at": new_task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    allowed_statuses = {"Pending", "In Progress", "Completed"}
    if task.status not in allowed_statuses:
        raise HTTPException(status_code=422, detail=f"Status must be one of: {', '.join(sorted(allowed_statuses))}")
    item = db.query(Task).filter(Task.id == task_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")
    item.status = task.status
    db.commit()
    db.refresh(item)
    return {"message": "Task updated successfully", "task": {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "priority": item.priority,
        "department": item.department,
        "status": item.status,
        "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None,
    }}


@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    return [project_dict(project) for project in db.query(Project).order_by(Project.id.desc()).all()]


@app.post("/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(
        name=project.name.strip(),
        repository_url=project.repository_url.strip() if project.repository_url else None,
        language=project.language.strip(),
        build_tool=project.build_tool.strip(),
        status="Connected",
        created_at=datetime.utcnow(),
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": "Project connected successfully", "project": project_dict(new_project)}


@app.post("/projects/analyze")
def analyze_project(payload: ProjectAnalyze, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    analysis = analyze_project_files(payload.files)
    project.status = "Analyzed"
    db.commit()
    return {"project": project_dict(project), "analysis": analysis}


@app.post("/builds/analyze")
def analyze_build(payload: BuildAnalyze, db: Session = Depends(get_db)):
    log = payload.log_text.strip()
    failed = bool(re.search(r"BUILD FAILURE|\[ERROR\]|FAILURE", log, re.IGNORECASE))
    result = explain_error_text(log) if failed else {
        "error_type": None,
        "root_cause": "No build failure detected.",
        "explanation": "The supplied log indicates a successful or informational build run.",
        "suggestions": ["Keep the passing build as a baseline.", "Publish test and artifact results in CI/CD."],
    }
    run = BuildRun(
        project_id=payload.project_id,
        status="Failed" if failed else "Passed",
        summary=result["root_cause"],
        error_type=result["error_type"],
        raw_log=log,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {"build": build_dict(run), "analysis": result}


@app.get("/builds")
def get_builds(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(BuildRun).order_by(BuildRun.id.desc())
    if project_id:
        query = query.filter(BuildRun.project_id == project_id)
    return [build_dict(run) for run in query.limit(20).all()]


@app.post("/ai/explain")
def explain_error(payload: ExplainError):
    return {"analysis": explain_error_text(payload.error_text)}


@app.get("/github/inspect")
def inspect_github(repo_url: str):
    parsed = urlparse(repo_url)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise HTTPException(status_code=422, detail="Only public GitHub repository URLs are supported.")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise HTTPException(status_code=422, detail="Use a repository URL such as https://github.com/owner/repository.")
    owner, repo = parts[0], parts[1].removesuffix(".git")
    request = Request(f"https://api.github.com/repos/{owner}/{repo}", headers={"Accept": "application/vnd.github+json", "User-Agent": "NexusOps-AI"})
    try:
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"GitHub inspection failed: {exc}") from exc
    return {
        "name": data.get("full_name"),
        "description": data.get("description"),
        "default_branch": data.get("default_branch"),
        "stars": data.get("stargazers_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "language": data.get("language"),
        "updated_at": data.get("updated_at"),
        "html_url": data.get("html_url"),
    }
