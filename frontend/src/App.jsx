import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const demoLog = `[INFO] Scanning for projects...
[ERROR] Failed to execute goal on project billing-service
[ERROR] DependencyResolutionException: Could not resolve artifact
[ERROR] BUILD FAILURE`;

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function App() {
  const [activeView, setActiveView] = useState("overview");
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [builds, setBuilds] = useState([]);
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("Medium");

  const [projectName, setProjectName] = useState("billing-service");
  const [repoUrl, setRepoUrl] = useState("https://github.com/example/billing-service");
  const [projectFiles, setProjectFiles] = useState("pom.xml, src/main/java/App.java, src/test/java/AppTest.java, .github/workflows/build.yml");
  const [projectAnalysis, setProjectAnalysis] = useState(null);

  const [logText, setLogText] = useState(demoLog);
  const [buildAnalysis, setBuildAnalysis] = useState(null);
  const [errorText, setErrorText] = useState("Could not resolve artifact com.example:payments-core:jar:2.1.0");
  const [errorAnalysis, setErrorAnalysis] = useState(null);
  const [githubUrl, setGithubUrl] = useState("https://github.com/sunkinani8-max/NexusOps-AI");
  const [githubData, setGithubData] = useState(null);

  const loadData = async () => {
    try {
      const [taskData, projectData, buildData] = await Promise.all([
        api("/tasks"),
        api("/projects"),
        api("/builds"),
      ]);
      setTasks(taskData);
      setProjects(projectData);
      setBuilds(buildData);
    } catch (error) {
      setNotice(error.message);
    }
  };

  useEffect(() => { loadData(); }, []);

  const stats = useMemo(() => ({
    requests: tasks.length,
    active: tasks.filter((task) => task.status !== "Completed").length,
    projects: projects.length,
    failedBuilds: builds.filter((build) => build.status === "Failed").length,
  }), [tasks, projects, builds]);

  const createTask = async (event) => {
    event.preventDefault();
    if (!title.trim() || !description.trim()) return setNotice("Enter both a request title and description.");
    setBusy(true);
    try {
      await api("/tasks", { method: "POST", body: JSON.stringify({ title, description, priority }) });
      setTitle(""); setDescription(""); setPriority("Medium"); setNotice("Request routed successfully."); await loadData();
    } catch (error) { setNotice(error.message); } finally { setBusy(false); }
  };

  const updateTask = async (id, status) => {
    try { await api(`/tasks/${id}`, { method: "PUT", body: JSON.stringify({ status }) }); await loadData(); }
    catch (error) { setNotice(error.message); }
  };

  const connectProject = async (event) => {
    event.preventDefault();
    setBusy(true);
    try {
      const data = await api("/projects", { method: "POST", body: JSON.stringify({ name: projectName, repository_url: repoUrl, language: "Java", build_tool: "Maven" }) });
      setNotice("Project connected. Ready for analysis.");
      await loadData();
      setProjectAnalysis({ project: data.project, analysis: null });
    } catch (error) { setNotice(error.message); } finally { setBusy(false); }
  };

  const analyzeProject = async () => {
    if (!projects[0]) return setNotice("Connect a project first.");
    setBusy(true);
    try {
      const data = await api("/projects/analyze", { method: "POST", body: JSON.stringify({ project_id: projects[0].id, files: projectFiles.split(",").map((file) => file.trim()).filter(Boolean) }) });
      setProjectAnalysis(data); setNotice("Project analysis completed."); await loadData();
    } catch (error) { setNotice(error.message); } finally { setBusy(false); }
  };

  const analyzeBuild = async () => {
    setBusy(true);
    try {
      const data = await api("/builds/analyze", { method: "POST", body: JSON.stringify({ project_id: projects[0]?.id || null, log_text: logText }) });
      setBuildAnalysis(data); setNotice("Build log analyzed."); await loadData();
    } catch (error) { setNotice(error.message); } finally { setBusy(false); }
  };

  const explainError = async () => {
    setBusy(true);
    try { const data = await api("/ai/explain", { method: "POST", body: JSON.stringify({ error_text: errorText }) }); setErrorAnalysis(data.analysis); setNotice("AI-style explanation generated."); }
    catch (error) { setNotice(error.message); } finally { setBusy(false); }
  };

  const inspectGithub = async () => {
    setBusy(true);
    try { const data = await api(`/github/inspect?repo_url=${encodeURIComponent(githubUrl)}`); setGithubData(data); setNotice("GitHub repository inspected."); }
    catch (error) { setNotice(error.message); } finally { setBusy(false); }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">N</div><div><strong>NexusOps</strong><span>AI OPERATIONS PLATFORM</span></div></div>
        <nav>
          <button className={activeView === "overview" ? "nav-item active" : "nav-item"} onClick={() => setActiveView("overview")}><span>◈</span> Command Center</button>
          <button className={activeView === "devops" ? "nav-item active" : "nav-item"} onClick={() => setActiveView("devops")}><span>⌘</span> DevOps Lab</button>
          <button className={activeView === "requests" ? "nav-item active" : "nav-item"} onClick={() => setActiveView("requests")}><span>≡</span> Requests</button>
        </nav>
        <div className="sidebar-bottom"><div className="status-dot"></div><div><strong>System Online</strong><small>API + database connected</small></div></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div><p className="eyebrow">NEXUSOPS AI / WORKSPACE</p><h1>{activeView === "devops" ? "Intelligent DevOps Lab" : activeView === "requests" ? "Operations Requests" : "Command Center"}</h1></div><div className="topbar-meta"><span>v3.0.0</span><span className="live-pill"><i></i> LIVE</span></div></header>
        {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice("")}>×</button></div>}

        {activeView === "overview" && <>
          <section className="hero-panel"><div><p className="eyebrow cyan">DETECT → UNDERSTAND → FIX → DEPLOY</p><h2>One intelligent layer across your software delivery lifecycle.</h2><p>Connect projects, inspect build health, understand errors, and route operational work from a single developer-focused platform.</p></div><div className="hero-orbit"><div className="orbit-line"></div><div className="orbit-core">AI<br /><small>RAG READY</small></div><span className="orbit-node n1">CODE</span><span className="orbit-node n2">BUILD</span><span className="orbit-node n3">GIT</span><span className="orbit-node n4">SHIP</span></div></section>
          <section className="stat-grid"><Stat label="Open Requests" value={stats.active} accent="cyan" /><Stat label="Connected Projects" value={stats.projects} accent="violet" /><Stat label="Build Failures" value={stats.failedBuilds} accent="red" /><Stat label="Total Requests" value={stats.requests} accent="blue" /></section>
          <section className="dashboard-grid"><div className="panel"><PanelTitle eyebrow="WORKFLOW" title="Request routing" /><form onSubmit={createTask} className="form-grid"><label>Request title<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Production access request" /></label><label>Description<textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Describe the operational issue..." /></label><label>Priority<select value={priority} onChange={(event) => setPriority(event.target.value)}><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select></label><button className="primary-button" disabled={busy}>{busy ? "Routing..." : "Create & classify request"}</button></form></div><div className="panel"><PanelTitle eyebrow="PIPELINE" title="Intelligent delivery flow" /><div className="pipeline"><PipelineStep number="01" title="Project connected" text="Source and metadata" /><PipelineStep number="02" title="Build analyzed" text="Logs and dependencies" active /><PipelineStep number="03" title="Root cause explained" text="AI-assisted guidance" /><PipelineStep number="04" title="Developer action" text="Fix, test, deploy" /></div></div></section>
        </>}

        {activeView === "devops" && <>
          <section className="devops-intro"><div><p className="eyebrow cyan">JAVA / MAVEN / GIT / AI</p><h2>Turn build signals into developer action.</h2><p>These modules give your project a working demonstration of the DevOps architecture shown in the presentation.</p></div><div className="module-badges"><span>Project Analyzer</span><span>Build Assistant</span><span>AI Explainer</span><span>Git Assistant</span></div></section>
          <section className="devops-grid"><div className="panel"><PanelTitle eyebrow="01 / PROJECT ANALYZER" title="Connect a Java project" /><form onSubmit={connectProject} className="form-grid"><label>Project name<input value={projectName} onChange={(event) => setProjectName(event.target.value)} /></label><label>Repository URL<input value={repoUrl} onChange={(event) => setRepoUrl(event.target.value)} /></label><label>Known files <textarea value={projectFiles} onChange={(event) => setProjectFiles(event.target.value)} /></label><div className="button-row"><button className="primary-button" disabled={busy}>{busy ? "Connecting..." : "Connect project"}</button><button type="button" className="secondary-button" onClick={analyzeProject} disabled={busy || !projects.length}>Analyze structure</button></div></form>{projectAnalysis?.analysis && <AnalysisCard title="Project analysis" data={projectAnalysis.analysis} />}</div><div className="panel"><PanelTitle eyebrow="02 / BUILD ASSISTANT" title="Analyze a Maven log" /><textarea className="log-editor" value={logText} onChange={(event) => setLogText(event.target.value)} /><button className="primary-button full" onClick={analyzeBuild} disabled={busy}>{busy ? "Analyzing..." : "Run build analysis"}</button>{buildAnalysis?.analysis && <AnalysisCard title={`${buildAnalysis.build.status} build`} data={buildAnalysis.analysis} />}</div></section>
          <section className="devops-grid"><div className="panel"><PanelTitle eyebrow="03 / AI ASSISTANT" title="Explain an error" /><textarea className="log-editor compact" value={errorText} onChange={(event) => setErrorText(event.target.value)} /><button className="violet-button full" onClick={explainError} disabled={busy}>Generate explanation</button>{errorAnalysis && <AnalysisCard title={errorAnalysis.error_type} data={errorAnalysis} violet />}</div><div className="panel"><PanelTitle eyebrow="04 / GIT ASSISTANT" title="Inspect a public GitHub repo" /><label>Repository URL<input value={githubUrl} onChange={(event) => setGithubUrl(event.target.value)} /></label><button className="secondary-button full" onClick={inspectGithub} disabled={busy}>Inspect repository</button>{githubData && <div className="repo-result"><strong>{githubData.name}</strong><p>{githubData.description || "No repository description"}</p><div className="repo-meta"><span>Language: {githubData.language || "—"}</span><span>★ {githubData.stars}</span><span>Issues: {githubData.open_issues}</span></div></div>}</div></section>
        </>}

        {activeView === "requests" && <section className="panel requests-panel"><PanelTitle eyebrow="OPERATIONS / REQUEST DASHBOARD" title="Track and update requests" /><div className="request-list">{tasks.length === 0 ? <EmptyState /> : tasks.map((task) => <div className="request-row" key={task.id}><div><div className="request-title"><strong>{task.title}</strong><span className={`priority priority-${task.priority.toLowerCase()}`}>{task.priority}</span></div><p>{task.description}</p><small>{task.department} · {task.created_at}</small></div><div className="request-actions"><span className={`status status-${task.status.toLowerCase().replace(" ", "-")}`}>{task.status}</span><select value={task.status} onChange={(event) => updateTask(task.id, event.target.value)}><option>Pending</option><option>In Progress</option><option>Completed</option></select></div></div>)}</div></section>}

        <footer><span>NEXUSOPS AI // INTELLIGENT DEVOPS AUTOMATION</span><span>JAVA + AI + GIT + MAVEN + DEVOPS</span></footer>
      </main>
    </div>
  );
}

function Stat({ label, value, accent }) { return <div className={`stat-card ${accent}`}><span>{label}</span><strong>{value}</strong><small>LIVE SIGNAL</small></div>; }
function PanelTitle({ eyebrow, title }) { return <div className="panel-title"><p className="eyebrow">{eyebrow}</p><h3>{title}</h3></div>; }
function PipelineStep({ number, title, text, active }) { return <div className={active ? "pipeline-step active" : "pipeline-step"}><span>{number}</span><div><strong>{title}</strong><small>{text}</small></div></div>; }
function AnalysisCard({ title, data, violet }) { return <div className={violet ? "analysis-card violet" : "analysis-card"}><div className="analysis-heading"><span>{title}</span><b>AI</b></div><p><strong>Root cause:</strong> {data.root_cause}</p><p>{data.explanation}</p><ul>{data.suggestions?.map((item) => <li key={item}>{item}</li>)}</ul></div>; }
function EmptyState() { return <div className="empty-state"><strong>No requests yet</strong><span>Create a request from the Command Center.</span></div>; }

export default App;
