const API_BASE = "https://task3-lyd0.onrender.com/api/tasks";

const suggestList = document.getElementById("suggest-list");
const suggestEmpty = document.getElementById("suggest-empty");
const analyzeBtn = document.getElementById("analyze");
const bulkJson = document.getElementById("bulk-json");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const resultsEmpty = document.getElementById("results-empty");
const strategySelect = document.getElementById("strategy");
const formTask = document.getElementById("task-form");
const clearSuggestionsBtn = document.getElementById("clear-suggestions");
const clearBtn = document.getElementById("clear");
const basedOnSelect = document.getElementById("based_on");

// Utility to set status message
function setStatus(msg = "", err = false) {
  statusEl.textContent = msg;
  statusEl.style.color = err ? "var(--danger)" : "var(--muted)";
}

// Collect task data from form
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
  // Handle empty case
  if (!data.length) {
    resultsEmpty.style.display = "block";
    return;
  }
  resultsEmpty.style.display = "none";

  // Render each task
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

// Analyze tasks
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
    }
    catch (e) {
      setStatus("JSON Error: " + e.message, true);
      return;
    }
  }

  // Validate we have tasks
  if (!tasks.length) {
    setStatus("Please fill form or paste JSON", true);
    return;
  }

  // Send tasks to server
  try {
    const strat = strategySelect.value;

    const res = await fetch(`${API_BASE}/analyze/?strategy=${strat}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tasks)
    });

    // Await response
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Server Error");

    setStatus("Analysis complete.");
    // Render results
    renderResults(data.tasks);
  }
  catch (err) {
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
        <div class="muted">Strategy: ${t.strategy}</div>
      </div>
    `;
    suggestList.appendChild(li);
  });
}

async function suggest() {
  setStatus("Fetching suggestions...");

  // Fetch suggestions from server
  try {

    const res = await fetch(`${API_BASE}/suggest/`);
    // Await response
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Server Error");

    // Handle no suggestions
    if (!data.suggestions || !data.suggestions.length) {
      setStatus("No suggestions found.", true);
      return;
    }

    basedOnSelect.textContent=`Based on ${data.based_on}`

    setStatus("Suggestions loaded.");
    // Render suggestions
    renderSuggestions(data.suggestions);
  }
  catch (err) {
    setStatus("Suggest failed: " + err.message, true);
  }
}
const suggestBtn = document.getElementById("suggest");

// Prevent default form submission
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

clearSuggestionsBtn.addEventListener("click", (e) => {
  e.preventDefault();
  suggestList.innerHTML = "";
  suggestEmpty.style.display = "block";
  setStatus("");
});

clearBtn.addEventListener("click", (e) => {
  e.preventDefault();
  resultsEl.innerHTML = "";
  resultsEmpty.style.display = "block";
  bulkJson.value = "";
  strategySelect.value = "smart_balance";
  document.getElementById("title").value = "";
  document.getElementById("due_date").value = "";
  document.getElementById("estimated_hours").value = "";
  document.getElementById("importance").value = "";
  document.getElementById("dependencies").value = "";

  setStatus("");
});

window.addEventListener("beforeunload", (event) => {
  // Check if we have results visible
  if (resultsEl.children.length > 0) {
    event.preventDefault();
  }
});
