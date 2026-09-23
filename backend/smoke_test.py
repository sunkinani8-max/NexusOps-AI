import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp(suffix='.db')}"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

assert client.get("/health").json()["status"] == "healthy"

request = client.post("/tasks", json={"title": "Laptop issue", "description": "WiFi is not working", "priority": "High"})
assert request.status_code == 200
assert request.json()["task"]["department"] == "IT"

project = client.post("/projects", json={"name": "billing-service", "repository_url": "https://github.com/example/billing-service"})
assert project.status_code == 200
project_id = project.json()["project"]["id"]

analysis = client.post("/projects/analyze", json={"project_id": project_id, "files": ["pom.xml", "src/main/java/App.java", "src/test/java/AppTest.java", ".github/workflows/build.yml"]})
assert analysis.status_code == 200
assert analysis.json()["analysis"]["signals"]["maven"] is True
assert analysis.json()["analysis"]["signals"]["ci_cd"] is True

build = client.post("/builds/analyze", json={"project_id": project_id, "log_text": "[ERROR] DependencyResolutionException: Could not resolve artifact\n[ERROR] BUILD FAILURE"})
assert build.status_code == 200
assert build.json()["build"]["status"] == "Failed"
assert build.json()["analysis"]["error_type"] == "Dependency resolution"

explanation = client.post("/ai/explain", json={"error_text": "cannot find symbol"})
assert explanation.status_code == 200
assert explanation.json()["analysis"]["error_type"] == "Compilation failure"

print("backend smoke test passed")
