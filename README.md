# 🚀 NexusOps AI
### ⚙️ Intelligent DevOps Automation & Developer Assistance Platform

**Detect · Understand · Fix · Deliver**

NexusOps AI is a developer-focused platform that combines operational request management with Java/Maven project analysis, build-log troubleshooting, GitHub repository inspection, and account administration.


## 🧭 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🖼️ Application Screenshots](#️-application-screenshots)
- [🧰 Technology Stack](#-technology-stack)
- [🏗️ System Architecture](#️-system-architecture)
- [📁 Project Structure](#-project-structure)
- [⚡ Installation and Setup](#-installation-and-setup)
- [▶️ Demonstration Workflow](#️-demonstration-workflow)
- [⚠️ Current Limitations](#️-current-limitations)
- [🔭 Future Enhancements](#-future-enhancements)

## 🎯 Overview

NexusOps AI provides a centralized workspace for operational requests and common DevOps analysis tasks. It combines project structure analysis, Maven build-log troubleshooting, GitHub repository inspection, profile settings, and administrator user-role management.

## ✨ Key Features

- 🖥️ **Command Center:** Create, classify, prioritize, and track operational requests.
- 🔧 **DevOps Lab:** Connect Java/Maven projects using repository and metadata fields.
- 🧩 **Project Structure Analysis:** Identify Java, Maven, testing, Docker, and CI/CD signals from submitted file lists.
- 🔍 **Build Log Analysis:** Detect common dependency, compilation, testing, and permission failures.
- 🤖 **AI-Style Assistance:** Generate pattern-based root-cause explanations and troubleshooting suggestions.
- 🐙 **GitHub Inspection:** Inspect public repository metadata through the GitHub REST API.
- 👤 **Profile & Security:** Manage profile details and access password-management controls.
- 🛡️ **User Administration:** Allow administrators to view accounts and manage user roles.


## 🧰 Technology Stack

| Component | Technologies |
|---|---|
| 🎨 Frontend | React 19, Vite, JavaScript, CSS |
| ⚙️ Backend | Python, FastAPI, Uvicorn, Pydantic |
| 🗃️ Database Access | SQLAlchemy |
| 🐘 Database | PostgreSQL or another supported SQLAlchemy-compatible database |
| 🔗 Repository Integration | GitHub REST API |
| 🔍 Build Analysis | Java/Maven project metadata and build-log pattern analysis |

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[👨‍💻 Developer] --> B[⚛️ React Frontend]
    B --> C[⚡ FastAPI Backend]
    C --> D[📋 Request Management]
    C --> E[🧩 Project Analysis]
    C --> F[🔍 Build Log Analysis]
    C --> G[🐙 GitHub REST API]
    C --> H[👤 Profile and Administration]
    D --> I[(🗃️ SQL Database)]
    E --> I
    F --> I
    H --> I
```

The React frontend communicates with the FastAPI backend. The backend handles request management, project and build analysis, GitHub metadata inspection, and account-related operations. SQLAlchemy provides database access.

## 📁 Project Structure

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
│       ├── login.png
│       ├── command-center.png
│       ├── devops-lab.png
│       ├── profile.png
│       └── admin-users.png
├── .env.example
├── .gitignore
└── README.md
```

## ⚡ Installation and Setup

### 📋 Prerequisites

- Python compatible with the backend dependencies
- Node.js and npm
- Git
- PostgreSQL, if configured as the application database

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sunkinani8-max/NexusOps-AI.git
cd NexusOps-AI
```

### 2️⃣ Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure the database connection according to your backend's environment settings.

Example PostgreSQL URL:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/nexusops
```

> 🔒 **Security:** Use your own credentials. Never commit real passwords, API keys, tokens, or production secrets.

### 3️⃣ Start the Backend

From the `backend/` directory:

```bash
uvicorn main:app --reload --port 8000
```

- 🌐 API: `http://127.0.0.1:8000`
- 📘 API Documentation: `http://127.0.0.1:8000/docs`

### 4️⃣ Install and Start the Frontend

Open another terminal at the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite. If supported by the frontend, configure `VITE_API_URL` in `frontend/.env` to point to the backend.

## ▶️ Demonstration Workflow

1. 🔐 Sign in or create an account.
2. 📋 Create an operational request in the Command Center.
3. 🔧 Connect a Java/Maven project in the DevOps Lab.
4. 🧩 Submit a project file list and run **Analyze Structure**.
5. 🔍 Paste a Maven failure log and run **Build Analysis**.
6. 🤖 Use the AI Assistant to explain a dependency or compilation error.
7. 🐙 Inspect a public GitHub repository using the Git Assistant.
8. 👤 Manage account details from the profile page.
9. 🛡️ If signed in as an administrator, manage account roles in User Administration.

## ⚠️ Current Limitations

- The current AI-style explanation engine is deterministic and pattern-based; it is not a live LLM integration.
- Project structure analysis uses the supplied file list rather than executing or fully scanning an arbitrary repository.
- The application does not execute arbitrary Maven commands or automatically modify source code.
- Production deployment requires appropriate authentication, secret management, database configuration, and security controls.

## 🔭 Future Enhancements

- 🧠 Integrate an LLM or retrieval-augmented generation (RAG) provider.
- 🔐 Add secure, sandboxed build execution with explicit developer approval.
- 🧪 Introduce automated testing and broader CI/CD integrations.
- 📊 Add audit logs, monitoring, and deployment workflows.
- 📈 Improve project analytics and build-history visualizations.

---

<p align="center">

**🚀 NexusOps AI**  
*Intelligent assistance for developer and DevOps workflows.*

</p>
