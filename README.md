# 🚀 NexusOps AI
### Intelligent DevOps Automation & Developer Assistance Platform

NexusOps AI is an intelligent developer and DevOps assistant that combines operational request management with a Java/Maven analysis workspace. It helps developers inspect project structures, analyze build logs, identify common failures, and understand possible next steps through a centralized dashboard.

<p align="center">
  <img src="docs/screenshots/command-center.png" alt="NexusOps AI Command Center" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" alt="React 19">
  <img src="https://img.shields.io/badge/Python-Backend-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vite-Frontend-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
</p>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Application Screenshots](#-application-screenshots)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Installation and Setup](#-installation-and-setup)
- [Demonstration Workflow](#-demonstration-workflow)
- [Current Limitations](#-current-limitations)
- [Future Enhancements](#-future-enhancements)

## 🎯 Overview

NexusOps AI provides a centralized workspace for operational requests and common DevOps analysis tasks. It connects project metadata, build-log analysis, repository inspection, and request tracking in one application.

The project demonstrates how developer-support workflows can be organized into a single interface, with a backend API and persistent database.

## ✨ Key Features

### 🖥️ Command Center
- Create, classify, prioritize, and track operational requests.
- View recent build outcomes and request statuses.
- Monitor activity through a centralized dashboard.

### 🔧 DevOps Lab
- Connect a Java/Maven project using repository and metadata fields.
- Analyze project file lists for Java, Maven, testing, Docker, and CI/CD indicators.
- Analyze Maven-style build logs.
- Detect common dependency, compilation, testing, and permission failures.

### 🤖 AI-Style Build Assistance
- Generate pattern-based root-cause explanations.
- Receive troubleshooting suggestions for common build errors.
- Identify likely next steps from the supplied error logs.

### 🐙 GitHub Repository Inspection
- Inspect public GitHub repository metadata using the GitHub REST API.

### 📋 Request Management
- Track operational requests through Pending, In Progress, and Completed states.
- Organize requests by classification and priority.

## 📸 Application Screenshots

Add screenshots captured from your running application to the `docs/screenshots/` folder.

### Command Center
![NexusOps AI Command Center](docs/screenshots/command-center.png)

### DevOps Lab
![NexusOps AI DevOps Lab](docs/screenshots/devops-lab.png)

### Request Management
![NexusOps AI Request Management](docs/screenshots/requests.png)

> Replace these placeholder images with genuine screenshots from your application. The images will appear after the corresponding files are committed to GitHub.

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React 19, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Database layer | SQLAlchemy |
| Database | PostgreSQL or another supported SQLAlchemy-compatible database |
| Repository integration | GitHub REST API |
| Build analysis | Java/Maven project metadata and log analysis |

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[Developer] --> B[React Dashboard]
    B --> C[FastAPI Backend]
    C --> D[Request Management]
    C --> E[Project Structure Analysis]
    C --> F[Build Log Analysis]
    C --> G[GitHub REST API]
    D --> H[(SQL Database)]
    E --> H
    F --> H
    G --> C
```

The React frontend communicates with the FastAPI backend. The backend coordinates request management, project analysis, build-log analysis, and GitHub metadata inspection, while SQLAlchemy provides database access.

## 📂 Project Structure

```text
NexusOps-AI/
├── backend/
│   ├── database.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── ...
├── docs/
│   └── screenshots/
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the application:

- Python 3.10 or a compatible version for the backend dependencies
- Node.js and npm
- PostgreSQL, if using PostgreSQL as the database
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/sunkinani8-max/NexusOps-AI.git
cd NexusOps-AI
```

### 2. Configure the Backend

Create and activate a Python virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure the database connection in the backend environment file according to your actual application configuration.

Example PostgreSQL URL:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/nexusops
```

> Use your own local credentials. Never commit real passwords, API keys, tokens, or production secrets.

### 3. Start the Backend

From the `backend/` directory, run:

```bash
uvicorn main:app --reload --port 8000
```

Backend API:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 4. Configure and Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

If your frontend supports a configurable API URL, set it in `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Open the local URL printed by Vite in your terminal.

## ▶️ Demonstration Workflow

1. Open the Command Center and create an operational request.
2. Check the request classification and priority.
3. Open the DevOps Lab and connect a Java/Maven project.
4. Enter a comma-separated project file list and select **Analyze Structure**.
5. Paste a Maven build failure log and run **Build Analysis**.
6. Use the AI Assistant to request an explanation of a dependency or compilation error.
7. Use the Git Assistant to inspect a public GitHub repository.
8. Open Requests and update a request through its supported lifecycle states.

## ⚠️ Current Limitations

- The current AI-style explanation engine is deterministic and pattern-based; it is not evidence of a live LLM integration.
- Project structure analysis uses submitted file-list information rather than executing or fully scanning an arbitrary repository.
- The application does not execute arbitrary Maven commands or automatically modify source code.
- Production deployment requires appropriate authentication, secret management, database configuration, and security controls.

## 🚀 Future Enhancements

- Integrate an LLM or retrieval-augmented generation (RAG) provider for richer troubleshooting.
- Add secure, sandboxed build execution with explicit developer approval.
- Introduce automated test execution and richer CI/CD integrations.
- Add detailed audit logs, monitoring, and deployment workflows.
- Improve project analytics and build history visualizations.

---

<p align="center">
  <strong>NexusOps AI</strong><br>
  Intelligent assistance for developer and DevOps workflows.
</p>
