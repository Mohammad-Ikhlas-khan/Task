const API_BASE = "http://127.0.0.1:8000/api/tasks";

const suggestList = document.getElementById("suggest-list");
const suggestEmpty = document.getElementById("suggest-empty");
const analyzeBtn = document.getElementById("analyze");
const bulkJson = document.getElementById("bulk-json");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const resultsEmpty = document.getElementById("results-empty");
const strategySelect = document.getElementById("strategy");
const strategySuggestSelect = document.getElementById("strategy-suggest");
const formTask = document.getElementById("task-form");

function setStatus(msg, err = false) {
  statusEl.textContent = msg;
  statusEl.style.color = err ? "var(--danger)" : "var(--muted)";
}

function collectFormTask() {
  const title = document.getElementById("title").value.trim();
  const due_date = document.getElementById("due_date").value;
  const estimated_hours = Number(document.getElementById("estimated_hours").value);
  const importance = Number(document.getElementById("importance").value);
  const deps = document.getElementById("dependencies").value.trim();

  if (!title || !due_date) return null;

  return {
    title,
    due_date,
    estimated_hours,
    importance,
    dependencies: deps ? deps.split(",").map(s => s.trim()) : []
  };
}

function renderResults(data) {
  resultsEl.innerHTML = "";
  if (!data.length) {
    resultsEmpty.style.display = "block";
    return;
  }
  resultsEmpty.style.display = "none";

  data.forEach(t => {
    const li = document.createElement("li");
    li.className = "task-item";
    li.innerHTML = `
      <div class="task-left">
        <strong>${t.title}</strong>
        <div class="muted">${t.due_date} • Effort ${t.estimated_hours}h • Importance ${t.importance}</div>
        <div class="explanation">${t.explanation || ""}</div>
      </div>
      <div>
        <div class="badge high">Score: ${t.score.toFixed(1)}</div>
      </div>
    `;
    resultsEl.appendChild(li);
  });
}

async function analyze() {
  setStatus("Analyzing...");

  let tasks = [];

  // form task
  const formTask = collectFormTask();
  if (!formTask && !bulkJson.value.trim()) {
    setStatus("Please fill form or paste JSON", true);
    return; // <--- Ensure it just returns, not throws
  }
  if (formTask) tasks.push(formTask);

  // json input
  const raw = bulkJson.value.trim();
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) throw new Error("JSON must be an array");
      tasks = tasks.concat(parsed);
    } catch (e) {
      setStatus("JSON Error: " + e.message, true);
      return;
    }
  }

  if (!tasks.length) {
    setStatus("Please fill form or paste JSON", true);
    return;
  }

  try {
    const strat = strategySelect.value;

    const res = await fetch(`${API_BASE}/analyze/?strategy=${strat}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tasks)
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Server Error");

    setStatus("Analysis complete.");
    console.log("BACKEND RESPONSE:", data);
    for (let i = 0; i < data.tasks.length; i++) {
      console.log(`Task: ${data.tasks[i].title}, Score: ${data.tasks[i].score}`);
    }

    renderResults(data.tasks);

  } catch (err) {
    setStatus("Analyze failed: " + err.message, true);
  }
}

function renderSuggestions(data) {
  suggestList.innerHTML = "";
  if (!data.length) {
    suggestEmpty.style.display = "block";
    return;
  }
  suggestEmpty.style.display = "none";

  data.forEach(t => {
    const li = document.createElement("li");
    li.className = "task-item";
    li.innerHTML = `
      <div class="task-left">
        <strong>${t.title}</strong>
        <div class="muted">${t.due_date} • Effort ${t.estimated_hours}h • Importance ${t.importance}</div>
        <div class="explanation">${t.explanation || ""}</div>
      </div>
      <div>
        <div class="badge high">Score: ${t.score.toFixed(1)}</div>
      </div>
    `;
    suggestList.appendChild(li);
  });
}

async function suggest() {
  setStatus("Fetching suggestions...");

  try {
    const strat = strategySuggestSelect.value;

    const res = await fetch(`${API_BASE}/suggest/?strategy=${strat}`);
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Server Error");

    if (!data.suggestions || !data.suggestions.length) {
      setStatus("No suggestions found.", true);
      return;
    }

    setStatus("Suggestions loaded.");
    renderSuggestions(data.suggestions);

  } catch (err) {
    setStatus("Suggest failed: " + err.message, true);
  }
}
const suggestBtn = document.getElementById("suggest");

if (formTask) {
  formTask.addEventListener("submit", (e) => {
    e.preventDefault();
  });
}


analyzeBtn.addEventListener("click", (e) => {
  e.preventDefault();
  analyze();
});

suggestBtn.addEventListener("click", (e) => {
  e.preventDefault();
  suggest();
});


window.addEventListener("beforeunload", (event) => {
  // Check if we have results visible
  if (resultsEl.children.length > 0) {
    event.preventDefault();
    event.returnValue = "Analysis results are visible. Are you sure you want to leave?";
  }
});
