import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {

  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [loading, setLoading] = useState(false);

  const loadTasks = async () => {

    try {

      const response = await fetch(`${API}/tasks`);

      const data = await response.json();

      setTasks(data);

    } catch (error) {

      console.error("Error loading tasks:", error);

    }

  };


  useEffect(() => {

    loadTasks();

  }, []);


  const createTask = async (event) => {
  event.preventDefault();

  if (!title.trim() || !description.trim()) {
    alert("Please enter a title and description.");
    return;
  }

  setLoading(true);

  const requestData = {
    title: title.trim(),
    description: description.trim(),
    priority: priority
  };

  console.log("Sending to NexusOps:", requestData);

  try {
    const response = await fetch("http://127.0.0.1:8000/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(requestData)
    });

    console.log("Backend status:", response.status);

    const data = await response.json();

    console.log("Backend response:", data);

    if (!response.ok) {
      throw new Error(
        data.detail
          ? JSON.stringify(data.detail)
          : "Backend rejected the request"
      );
    }

    setTitle("");
    setDescription("");
    setPriority("Medium");

    await loadTasks();

  } catch (error) {
    console.error("NexusOps error:", error);

    alert(
      "NexusOps request failed.\n\n" +
      error.message
    );

  } finally {
    setLoading(false);
  }
};


  const updateTask = async (id, status) => {

    try {

      const response = await fetch(
        `${API}/tasks/${id}?status=${encodeURIComponent(status)}`,
        {
          method: "PUT"
        }
      );

      if (!response.ok) {

        throw new Error("Failed to update task");

      }

      await loadTasks();

    } catch (error) {

      console.error(error);

      alert("Could not update the task.");

    }

  };


  return (

    <div className="app">

      <header className="header">

        <div>

          <h1>NexusOps AI</h1>

          <p>
            Intelligent Business Workflow Platform
          </p>

        </div>

        <div className="online">
          ● System Online
        </div>

      </header>


      <main>

        <section className="hero">

          <div>

            <p className="eyebrow">
              AI OPERATIONS PLATFORM
            </p>

            <h2>
              Automate your business workflows.
            </h2>

            <p className="hero-text">
              NexusOps AI receives business requests,
              analyzes them and automatically routes
              them to the appropriate department.
            </p>

          </div>

        </section>


        <section className="dashboard">


          <div className="card">

            <div className="card-header">

              <div>

                <h2>Create Request</h2>

                <p>
                  Submit a new operational request.
                </p>

              </div>

            </div>


            <form onSubmit={createTask}>

              <label>
                Request Title
              </label>

              <input
                type="text"
                placeholder="Example: Laptop not working"
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
              />


              <label>
                Description
              </label>

              <textarea
                placeholder="Describe the request or problem..."
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
              />


              <label>
                Priority
              </label>

              <select
                value={priority}
                onChange={(event) =>
                  setPriority(event.target.value)
                }
              >

                <option value="Low">
                  Low
                </option>

                <option value="Medium">
                  Medium
                </option>

                <option value="High">
                  High
                </option>

                <option value="Critical">
                  Critical
                </option>

              </select>


              <button
                type="submit"
                disabled={loading}
              >

                {loading
                  ? "Creating Request..."
                  : "Create Request"}

              </button>

            </form>

          </div>


          <div className="card">

            <h2>AI Workflow</h2>

            <p className="card-description">
              Every request passes through the NexusOps
              workflow engine.
            </p>


            <div className="workflow">

              <div className="workflow-item">

                <span>01</span>

                <div>
                  <strong>
                    Request Received
                  </strong>

                  <small>
                    New business request
                  </small>
                </div>

              </div>


              <div className="arrow">
                ↓
              </div>


              <div className="workflow-item">

                <span>02</span>

                <div>
                  <strong>
                    AI Classification
                  </strong>

                  <small>
                    Understand the request
                  </small>
                </div>

              </div>


              <div className="arrow">
                ↓
              </div>


              <div className="workflow-item">

                <span>03</span>

                <div>
                  <strong>
                    Department Detection
                  </strong>

                  <small>
                    Identify responsible team
                  </small>
                </div>

              </div>


              <div className="arrow">
                ↓
              </div>


              <div className="workflow-item">

                <span>04</span>

                <div>
                  <strong>
                    Task Assignment
                  </strong>

                  <small>
                    Start the workflow
                  </small>
                </div>

              </div>

            </div>

          </div>

        </section>


        <section className="tasks">

          <div className="section-header">

            <div>

              <p className="eyebrow">
                OPERATIONS
              </p>

              <h2>
                Request Dashboard
              </h2>

            </div>

            <div className="task-count">

              {tasks.length} Requests

            </div>

          </div>


          {tasks.length === 0 ? (

            <div className="empty">

              <div className="empty-icon">
                📋
              </div>

              <h3>
                No requests yet
              </h3>

              <p>
                Create your first request above.
              </p>

            </div>

          ) : (

            <div className="task-list">

              {tasks.map((task) => (

                <div
                  className="task"
                  key={task.id}
                >

                  <div className="task-main">

                    <div className="task-title-row">

                      <h3>
                        {task.title}
                      </h3>

                      <span
                        className={`status status-${task.status
                          .toLowerCase()
                          .replace(" ", "-")}`}
                      >
                        {task.status}
                      </span>

                    </div>


                    <p>
                      {task.description}
                    </p>


                    <div className="tags">

                      <span>
                        Department: {task.department}
                      </span>

                      <span>
                        Priority: {task.priority}
                      </span>

                      <span>
                        Created: {task.created_at}
                      </span>

                    </div>

                  </div>


                  <div className="actions">

                    {task.status === "Pending" && (

                      <button
                        onClick={() =>
                          updateTask(
                            task.id,
                            "In Progress"
                          )
                        }
                      >
                        Start
                      </button>

                    )}


                    {task.status !== "Completed" && (

                      <button
                        onClick={() =>
                          updateTask(
                            task.id,
                            "Completed"
                          )
                        }
                      >
                        Complete
                      </button>

                    )}

                  </div>

                </div>

              ))}

            </div>

          )}

        </section>

      </main>


      <footer>

        <p>
          NexusOps AI • Intelligent Workflow Automation
        </p>

      </footer>

    </div>

  );

}

export default App;