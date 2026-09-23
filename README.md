# NexusOps AI

NexusOps AI is an intelligent developer and DevOps assistant that combines business request routing with a working Java/Maven analysis workspace. The application demonstrates the core lifecycle shown in the project presentation: connect a project, inspect its structure, analyze build logs, explain errors, and help the developer decide the next action.

## Implemented capabilities

- Create, classify, prioritize, and track operational requests.
- Persist requests, connected projects, and build runs in a SQL database.
- Connect a Java/Maven project using repository and metadata fields.
- Analyze a submitted project file list for Java, Maven, tests, Docker, and CI/CD signals.
- Analyze Maven-style build logs and detect common dependency, compilation, test, and permission failures.
- Generate deterministic, AI-style root-cause explanations and troubleshooting suggestions.
- Inspect public GitHub repository metadata through the GitHub REST API.
- Track recent build outcomes in the dashboard.
- Use a responsive React dashboard with Command Center, DevOps Lab, and Requests views.

## Technology stack

### Frontend

- React 19
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL or another SQLAlchemy-compatible database

## Project structure

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
├── .env.example
├── .gitignore
└── README.md
```

## Local setup

### 1. Configure the database

Create `backend/.env` from the example below. A local PostgreSQL database is recommended for the full project, but any SQLAlchemy-compatible database URL can be used.

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/nexusops
```

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000`. FastAPI documentation is available at `/docs`.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

To use a different backend URL, create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Demonstration flow

1. Open the Command Center and create an operational request.
2. Confirm that the request is automatically classified into a department.
3. Open the DevOps Lab and connect a Java/Maven project.
4. Enter a comma-separated project file list and run **Analyze structure**.
5. Paste a Maven failure log and run **Build analysis**.
6. Use **AI Assistant** to explain a dependency or compilation error.
7. Use **Git Assistant** to inspect a public GitHub repository.
8. Open Requests to update the request lifecycle from Pending to In Progress or Completed.

## Implementation boundary

The current AI explanation engine is deterministic and pattern-based. It is intentionally safe for a local demonstration and provides a clear integration seam for a future LLM or RAG provider. The current project does not execute arbitrary Maven commands or modify source code automatically. Those capabilities should be added with sandboxing, authentication, and explicit developer approval before production use.
