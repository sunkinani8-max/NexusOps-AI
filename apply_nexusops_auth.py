#!/usr/bin/env python3
"""Apply local NexusOps AI register/login and per-user data ownership.
Run from the NexusOps-AI project root: python3 /mnt/data/apply_nexusops_auth.py
"""
from pathlib import Path
import re, secrets, shutil, sys

ROOT = Path.cwd()
P = {
    'db': ROOT/'backend/database.py', 'main': ROOT/'backend/main.py',
    'app': ROOT/'frontend/src/App.jsx', 'css': ROOT/'frontend/src/App.css',
    'req': ROOT/'backend/requirements.txt', 'env': ROOT/'backend/.env'
}
for k in ('db','main','app','css','req'):
    if not P[k].is_file():
        sys.exit(f"Missing {P[k]}. First run: cd ~/Desktop/NexusOps-AI")
S = {k:P[k].read_text() for k in ('db','main','app','css','req')}
if 'def get_current_user(' in S['main'] and 'function AuthScreen(' in S['app']:
    print('Auth code already appears installed; no files changed.')
    sys.exit(0)
for k in ('db','main','app','css','req'):
    backup=P[k].with_name(P[k].name+'.before-auth')
    if not backup.exists(): shutil.copy2(P[k],backup)

def rep(s, old, new, label):
    if old not in s: raise RuntimeError('Could not safely update '+label+'; no files were written.')
    return s.replace(old,new,1)

db,main,app,css,req=(S[k] for k in ('db','main','app','css','req'))
# DB models: User + nullable owner_id fields, allowing migration of existing SQLite tables.
if 'import os' not in db: db='import os\n'+db
if 'class User(Base):' not in db:
    user_model='''\n\nclass User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


'''
    db=rep(db,'def get_db():',user_model+'def get_db():','User model')
owner='    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)\n'
# Add each ownership field only to the intended model.
def add_to_model(text, start, end, field):
    before, rest=text.split(start,1)
    if end and end in rest: body,after=rest.split(end,1); suffix=end+after
    else: body, suffix=rest,''
    if 'owner_id = Column' not in body:
        # insert after the created_at line in this model
        m=re.search(r'    created_at = Column\(DateTime, default=datetime\.utcnow\)\n',body)
        if not m: raise RuntimeError('Could not locate created_at in '+start)
        i=m.end(); body=body[:i]+field+body[i:]
    return before+start+body+suffix
if 'class Task(Base):' not in db or 'class Project(Base):' not in db or 'class BuildRun(Base):' not in db:
    raise RuntimeError('Unexpected database.py model structure; no files written.')
db=add_to_model(db,'class Task(Base):','class Project(Base):',owner)
db=add_to_model(db,'class Project(Base):','class BuildRun(Base):',owner)
db=add_to_model(db,'class BuildRun(Base):',None,owner)

# Main imports and schemas.
if 'from pwdlib import PasswordHash' not in main:
    main=rep(main,'from typing import Optional','from typing import Optional\nimport os\n\nimport jwt\nfrom pwdlib import PasswordHash','auth imports')
if 'HTTPBearer' not in main:
    main=rep(main,'from fastapi import Depends, FastAPI, HTTPException','from fastapi import Depends, FastAPI, HTTPException\nfrom fastapi.security import HTTPAuthorizationCredentials, HTTPBearer','bearer auth import')
if 'from database import Base, BuildRun, Project, Task, User, engine, get_db' not in main:
    main=rep(main,'from database import Base, BuildRun, Project, Task, engine, get_db','from database import Base, BuildRun, Project, Task, User, engine, get_db','User import')
if 'class RegisterInput(BaseModel):' not in main:
    schemas='''\n\nclass RegisterInput(BaseModel):
    username: str = Field(min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginInput(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)

'''
    main=rep(main,'# Existing business workflow classification',schemas+'# Existing business workflow classification','auth schemas')
# Migration creates new tables and adds missing nullable columns without dropping rows.
if 'def migrate_ownership_columns()' not in main:
    migration='''\n\ndef migrate_ownership_columns():
    from sqlalchemy import inspect, text
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table in ("tasks", "projects", "build_runs"):
            if table not in tables:
                continue
            columns = {col["name"] for col in inspect(engine).get_columns(table)}
            if "owner_id" not in columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN owner_id INTEGER"))

migrate_ownership_columns()

'''
    main=rep(main,'app.add_middleware(',migration+'app.add_middleware(','SQLite migration')
if 'def get_current_user(' not in main:
    auth='''\n\n# Authentication: JWT sessions and Argon2 password hashing.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "local-development-secret-change-this")
JWT_ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


def user_dict(user: User) -> dict:
    return {"id": user.id, "username": user.username, "email": user.email,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None}


def create_access_token(user: User) -> str:
    from datetime import timedelta
    now = datetime.utcnow()
    return jwt.encode({"sub": str(user.id), "email": user.email, "iat": now,
                       "exp": now + timedelta(days=7)}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
                     db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Please log in to continue.")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub", ""))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please log in again.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Account not found.")
    return user


@app.post("/auth/register")
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    username, email = payload.username.strip(), payload.email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if not username:
        raise HTTPException(status_code=422, detail="Username is required.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(username=username, email=email, hashed_password=password_hash.hash(payload.password))
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not create account. Try another email.")
    db.refresh(user)
    # Existing pre-account rows are assigned to the first account registering.
    for model in (Task, Project, BuildRun):
        db.query(model).filter(model.owner_id.is_(None)).update({model.owner_id: user.id}, synchronize_session=False)
    db.commit()
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user_dict(user)}


@app.post("/auth/login")
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not password_hash.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user_dict(user)}


@app.get("/auth/me")
def auth_me(current_user: User = Depends(get_current_user)):
    return {"user": user_dict(current_user)}

'''
    main=rep(main,'# Existing business workflow classification',auth+'\n# Existing business workflow classification','auth endpoints')
# Scope personal-data APIs to the logged-in user.
pairs=[
('def get_tasks(db: Session = Depends(get_db)):','def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('tasks = db.query(Task).order_by(Task.id.desc()).all()','tasks = db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.id.desc()).all()'),
('def create_task(task: TaskCreate, db: Session = Depends(get_db)):','def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('        title=task.title.strip(),','        owner_id=current_user.id,\n        title=task.title.strip(),'),
('def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):','def update_task(task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('item = db.query(Task).filter(Task.id == task_id).first()','item = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()'),
('def get_projects(db: Session = Depends(get_db)):','def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('db.query(Project).order_by(Project.id.desc()).all()','db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.id.desc()).all()'),
('def create_project(project: ProjectCreate, db: Session = Depends(get_db)):','def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('        name=project.name.strip(),','        owner_id=current_user.id,\n        name=project.name.strip(),'),
('def analyze_project(payload: ProjectAnalyze, db: Session = Depends(get_db)):','def analyze_project(payload: ProjectAnalyze, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('db.query(Project).filter(Project.id == payload.project_id).first()','db.query(Project).filter(Project.id == payload.project_id, Project.owner_id == current_user.id).first()'),
('def analyze_build(payload: BuildAnalyze, db: Session = Depends(get_db)):','def analyze_build(payload: BuildAnalyze, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('def get_builds(project_id: Optional[int] = None, db: Session = Depends(get_db)):','def get_builds(project_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):'),
('query = db.query(BuildRun).order_by(BuildRun.id.desc())','query = db.query(BuildRun).filter(BuildRun.owner_id == current_user.id).order_by(BuildRun.id.desc())'),
('        project_id=payload.project_id,','        project_id=payload.project_id,\n        owner_id=current_user.id,'),
]
for old,new in pairs:
    if old in main: main=main.replace(old,new,1)
    elif new not in main: raise RuntimeError('Could not safely patch backend near: '+old[:70])
# Guard build analysis from linking another account's project.
guard='''    if payload.project_id is not None:
        owned_project = db.query(Project).filter(Project.id == payload.project_id, Project.owner_id == current_user.id).first()
        if not owned_project:
            raise HTTPException(status_code=404, detail="Project not found")
'''
if guard not in main:
    main=rep(main,'    log = payload.log_text.strip()\n',guard+'    log = payload.log_text.strip()\n','build project ownership')

# Frontend token header.
old_api='''async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}'''
new_api='''async function api(path, options = {}) {
  const token = localStorage.getItem("nexusops_token");
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}'''
if old_api in app: app=app.replace(old_api,new_api,1)
elif 'localStorage.getItem("nexusops_token")' not in app: raise RuntimeError('Could not find frontend API helper.')
if 'const [user, setUser] = useState' not in app:
    app=rep(app,'  const [activeView, setActiveView] = useState("overview");','''  const [activeView, setActiveView] = useState("overview");
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("nexusops_user") || "null"); } catch { return null; }
  });''','frontend auth state')
app=app.replace('  useEffect(() => { loadData(); }, []);','  useEffect(() => { if (user) loadData(); }, [user]);',1)
if 'const handleAuthSuccess' not in app:
    app=rep(app,'  const stats = useMemo(() => ({','''  const handleAuthSuccess = (data) => {
    localStorage.setItem("nexusops_token", data.access_token);
    localStorage.setItem("nexusops_user", JSON.stringify(data.user));
    setUser(data.user);
    setNotice("Welcome to NexusOps AI.");
  };

  const logout = () => {
    localStorage.removeItem("nexusops_token");
    localStorage.removeItem("nexusops_user");
    setUser(null); setTasks([]); setProjects([]); setBuilds([]); setNotice("");
  };

  const stats = useMemo(() => ({''','frontend auth handlers')
app=rep(app,'  return (\n    <div className="app-shell">','  if (!user) return <AuthScreen onSuccess={handleAuthSuccess} />;\n\n  return (\n    <div className="app-shell">','frontend login gate')
app=rep(app,'<div className="topbar-meta"><span>v3.0.0</span><span className="live-pill"><i></i> LIVE</span></div>','<div className="topbar-meta"><span className="account-name">{user.username}</span><button className="logout-button" onClick={logout}>Log out</button><span>v3.0.0</span><span className="live-pill"><i></i> LIVE</span></div>','profile/logout header')
if 'function AuthScreen(' not in app:
    component=r'''
function AuthScreen({ onSuccess }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const submit = async (event) => {
    event.preventDefault(); setBusy(true); setMessage("");
    try {
      if (mode === "register") await api("/auth/register", { method: "POST", body: JSON.stringify({ username, email, password }) });
      const data = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      onSuccess(data);
    } catch (error) { setMessage(error.message || "Authentication failed."); }
    finally { setBusy(false); }
  };
  return <main className="auth-shell"><section className="auth-card">
    <div className="brand auth-brand"><div className="brand-mark">N</div><div><strong>NexusOps</strong><span>AI OPERATIONS PLATFORM</span></div></div>
    <p className="eyebrow cyan">YOUR PRIVATE WORKSPACE</p><h1>{mode === "login" ? "Welcome back" : "Create your account"}</h1>
    <p className="auth-subtitle">Manage your projects, requests, and build history in one place.</p>
    <div className="auth-tabs"><button type="button" className={mode === "login" ? "auth-tab selected" : "auth-tab"} onClick={() => {setMode("login");setMessage("");}}>Log in</button><button type="button" className={mode === "register" ? "auth-tab selected" : "auth-tab"} onClick={() => {setMode("register");setMessage("");}}>Create account</button></div>
    <form className="form-grid auth-form" onSubmit={submit}>
      {mode === "register" && <label>Username<input required minLength="2" maxLength="60" value={username} onChange={e=>setUsername(e.target.value)} placeholder="Your name" /></label>}
      <label>Email<input required type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" /></label>
      <label>Password<input required type="password" minLength={mode === "register" ? 8 : 1} autoComplete={mode === "register" ? "new-password" : "current-password"} value={password} onChange={e=>setPassword(e.target.value)} placeholder={mode === "register" ? "At least 8 characters" : "Your password"} /></label>
      {message && <p className="auth-message" role="alert">{message}</p>}
      <button className="primary-button" disabled={busy}>{busy ? "Please wait..." : mode === "login" ? "Log in securely" : "Create account"}</button>
    </form><small className="auth-note">Passwords are stored as secure hashes, not plain text.</small>
  </section></main>;
}

'''
    app=rep(app,'function Stat({ label, value, accent })',component+'function Stat({ label, value, accent })','AuthScreen component')
if '.auth-shell{' not in css:
    css += r'''

/* NexusOps account screens */
.auth-shell{min-height:100vh;display:grid;place-items:center;padding:28px;box-sizing:border-box;background:radial-gradient(circle at 15% 15%,rgba(0,229,255,.10),transparent 35%),radial-gradient(circle at 85% 80%,rgba(124,92,255,.12),transparent 35%),#0b0f19;color:#eef3ff}
.auth-card{width:min(100%,460px);box-sizing:border-box;padding:34px;border:1px solid rgba(130,155,200,.22);border-radius:22px;background:rgba(17,24,39,.96);box-shadow:0 24px 80px rgba(0,0,0,.35)}
.auth-brand{margin-bottom:32px}.auth-card h1{margin:10px 0;font-size:30px;letter-spacing:-.04em}.auth-subtitle{color:#a8b3c9;line-height:1.6;margin-bottom:22px}
.auth-tabs{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:5px;border-radius:12px;background:#0b1220;margin:20px 0}
.auth-tab{border:0;border-radius:9px;padding:11px;background:transparent;color:#a8b3c9;cursor:pointer}.auth-tab.selected{background:#1c2940;color:#fff}
.auth-form{gap:16px}.auth-form label{display:grid;gap:8px;color:#c8d3e7;font-size:13px}.auth-form input{width:100%;box-sizing:border-box;padding:12px 13px;border:1px solid #303d55;border-radius:10px;background:#0b1220;color:#fff;outline:none}.auth-form input:focus{border-color:#00e5ff}
.auth-message{margin:0;color:#ff9caa;font-size:13px}.auth-note{display:block;margin-top:20px;color:#8492ac;line-height:1.5}
.account-name{color:#d7e4fa;font-weight:600}.logout-button{border:1px solid #34425c;border-radius:8px;padding:7px 10px;background:#121b2c;color:#dce7f8;cursor:pointer}.logout-button:hover{border-color:#00e5ff}
@media(max-width:560px){.auth-card{padding:24px}.auth-card h1{font-size:25px}}
'''
# requirements and .env signing key.
packages=[line.strip() for line in req.splitlines() if line.strip()]
for package in ('PyJWT[crypto]','pwdlib[argon2]','python-multipart'):
    if package.lower() not in [x.lower() for x in packages]: packages.append(package)
req='\n'.join(packages)+'\n'
env=P['env'].read_text() if P['env'].exists() else ''
if not re.search(r'(?m)^JWT_SECRET_KEY=',env): env += ('' if not env or env.endswith('\n') else '\n')+'JWT_SECRET_KEY='+secrets.token_urlsafe(48)+'\n'
# Syntax check before writing.
compile(db,str(P['db']),'exec'); compile(main,str(P['main']),'exec')
for k,value in [('db',db),('main',main),('app',app),('css',css),('req',req),('env',env)]: P[k].write_text(value)
print('SUCCESS: authentication code added and original files backed up as *.before-auth')
print('Next: cd backend && python3 -m pip install -r requirements.txt && python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000')
print('Frontend: cd ~/Desktop/NexusOps-AI/frontend && npm run dev')
print('Then open http://localhost:5173 and register your first account.')
