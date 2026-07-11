const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 3000;
const DATA_FILE = path.join(__dirname, "data", "submissions.json");

// Ensure data directory exists
if (!fs.existsSync(path.join(__dirname, "data"))) {
  fs.mkdirSync(path.join(__dirname, "data"), { recursive: true });
}

// Initialize submissions file
if (!fs.existsSync(DATA_FILE)) {
  fs.writeFileSync(DATA_FILE, "[]", "utf-8");
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(__dirname));

// Helper: read submissions
function readSubmissions() {
  try {
    const raw = fs.readFileSync(DATA_FILE, "utf-8");
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

// Helper: write submissions
function writeSubmissions(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), "utf-8");
}

// API: Submit form
app.post("/api/submit", (req, res) => {
  const { name, phone, email, program, goal, message, coach, form_type, company, contact_name, event_type, attendees, preferred_date, budget, location } = req.body;

  if (form_type === "corporate_event") {
    if (!company || !contact_name || !email || !phone || !event_type || !attendees) {
      return res.status(400).json({ ok: false, error: "Missing required fields" });
    }
  } else {
    if (!name || !phone || !program || !goal) {
      return res.status(400).json({ ok: false, error: "Missing required fields" });
    }
  }

  const submission = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    form_type: form_type || "consultation",
    name: name || contact_name || "",
    phone,
    email: email || "",
    program: program || "",
    goal: goal || "",
    message: message || "",
    coach: coach || "",
    company: company || "",
    event_type: event_type || "",
    attendees: attendees || "",
    preferred_date: preferred_date || "",
    budget: budget || "",
    location: location || "",
    timestamp: new Date().toISOString(),
    ip: req.headers["x-forwarded-for"] || req.socket.remoteAddress,
  };

  const submissions = readSubmissions();
  submissions.unshift(submission);
  writeSubmissions(submissions);

  console.log(`[NEW SUBMISSION] ${submission.name} — ${submission.program} — ${submission.timestamp}`);
  res.json({ ok: true, id: submission.id });
});

// API: Get all submissions
app.get("/api/submissions", (req, res) => {
  const submissions = readSubmissions();
  res.json({ ok: true, count: submissions.length, data: submissions });
});

// API: Delete a submission
app.delete("/api/submissions/:id", (req, res) => {
  const { id } = req.params;
  let submissions = readSubmissions();
  const before = submissions.length;
  submissions = submissions.filter((s) => s.id !== id);
  if (submissions.length === before) {
    return res.status(404).json({ ok: false, error: "Not found" });
  }
  writeSubmissions(submissions);
  res.json({ ok: true });
});

// Admin page
app.get("/admin", (req, res) => {
  res.sendFile(path.join(__dirname, "admin.html"));
});

// Catch-all: serve index
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.listen(PORT, () => {
  console.log(`\n  Fitness Gurukul Server running at:\n`);
  console.log(`  Local:   http://localhost:${PORT}`);
  console.log(`  Admin:   http://localhost:${PORT}/admin`);
  console.log(`\n  Submissions stored in: data/submissions.json\n`);
});
