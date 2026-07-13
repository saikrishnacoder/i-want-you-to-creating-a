const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = Number(process.env.PORT || 3000);
const DATA_FILE = path.join(__dirname, "data", "submissions.json");

function loadEnvFile() {
  const envPath = path.join(__dirname, ".env");
  if (!fs.existsSync(envPath)) return;
  fs.readFileSync(envPath, "utf-8").split(/\r?\n/).forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) return;
    const index = line.indexOf("=");
    const key = line.slice(0, index).trim();
    const value = line.slice(index + 1).trim().replace(/^['"]|['"]$/g, "");
    if (key && process.env[key] == null) process.env[key] = value;
  });
}

loadEnvFile();

const CONTACT = {
  phone: "08042781491",
  whatsapp: "+917207113310",
  email: "contact@fitnessgurukul.co.in",
  address: "H.no.1-10/2, Lakshmi Nagar Colony, near Pochamma Temple, Manikonda, Hyderabad, 500089",
};

const CHAT_SUGGESTIONS = [
  "Which plan is best for weight loss?",
  "Compare Core, Prime and Signature",
  "Do you have running or Hyrox plans?",
  "Which coach is best for yoga?",
];

const PLANS = [
  { name: "Fitness Gurukul Core", tag: "1-on-1 Coaching", category: "core", summary: "Dedicated fitness and nutrition coach with hyper-personalized workout plans, tailored Indian nutrition, and weekly video check-ins.", price: "From INR 5,999/month", sessions: "1 session/week", points: ["Dedicated coach", "Custom meal plan", "Video check-ins", "In-person PT", "App check-in"] },
  { name: "Fitness Gurukul Prime", tag: "Advanced Coaching", category: "prime", summary: "Complete fitness and nutrition coaching with 3x/week in-person personal training, posture correction, nutrition planning, and mandatory app check-ins.", price: "From INR 9,500/month", sessions: "3 sessions/week", points: ["1:1 coach + PT", "Nutrition plan", "Video check-ins", "Structural assessment", "App check-in"] },
  { name: "Fitness Gurukul Signature", tag: "Intensive Coaching", category: "signature", summary: "Intensive transformation plan to build strength, correct movement, and transform physique with 5x/week in-person training.", price: "INR 15,999/month", sessions: "5 sessions/week", points: ["1:1 coach", "In-person PT", "Nutrition plan", "Structural assessment", "App check-in"] },
  { name: "Fitness Gurukul Endurance", tag: "Running Coaching", category: "endurance", summary: "Professional running coaching for beginners through advanced PR-seekers with periodized training, strength and conditioning, endurance nutrition, and race-day strategy.", price: "INR 1,199/month", sessions: "Virtual", points: ["Dedicated running coach", "Periodized running program", "Runner-specific S&C", "Endurance nutrition", "Race strategy", "Daily chat support"] },
  { name: "Fitness Gurukul Forge", tag: "Hyrox / OCR Prep", category: "forge", summary: "Functional fitness racing prep for Hyrox and OCR athletes with compounded S&C, engine building, grip strength, explosive power, and compromised running stamina.", price: "INR 999/month", sessions: "Virtual", points: ["Dedicated S&C coach", "Compounded S&C workouts", "Functional engine building", "Agility and grip strength", "Explosive power drills"] },
  { name: "Virtual 1:1 Elite Transformation", tag: "Weight Loss & Muscle Gain", category: "elite", summary: "Remote 1:1 fitness and nutrition coaching for weight loss, lean muscle gain, or lifestyle overhaul with hyper-personalized plans.", price: "From INR 1,999/month", sessions: "Virtual", points: ["Dedicated coach", "Custom workout plans", "Indian nutrition plan", "Video check-ins", "Daily chat support", "Progressive overload"] },
];

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

function normalizeChatText(value) {
  return String(value || "").trim().replace(/\s+/g, " ");
}

function chatContainsAny(text, words) {
  return words.some((word) => text.includes(word));
}

function planScore(plan, text) {
  const haystack = [
    plan.name,
    plan.tag,
    plan.category,
    plan.summary,
    plan.price,
    plan.sessions,
    plan.points.join(" "),
  ].join(" ").toLowerCase();
  const tokens = text.toLowerCase().split(/[^a-z0-9]+/).filter((token) => token.length > 2);
  let score = tokens.reduce((total, token) => total + (haystack.includes(token) ? 1 : 0), 0);
  if (chatContainsAny(text, ["weight", "fat", "loss", "slim", "transform", "muscle", "body", "lifestyle"]) && ["elite", "core", "prime", "signature"].includes(plan.category)) score += 3;
  if (chatContainsAny(text, ["home", "doorstep", "personal", "offline", "trainer", "pt", "in person", "session"]) && ["core", "prime", "signature"].includes(plan.category)) score += 3;
  if (chatContainsAny(text, ["run", "running", "marathon", "race", "endurance", "5k", "10k"]) && plan.category === "endurance") score += 6;
  if (chatContainsAny(text, ["hyrox", "ocr", "obstacle", "functional", "forge"]) && plan.category === "forge") score += 6;
  if (chatContainsAny(text, ["budget", "cheap", "low", "affordable", "online", "virtual"]) && ["elite", "forge", "endurance"].includes(plan.category)) score += 3;
  if (chatContainsAny(text, ["daily", "intense", "fast", "maximum", "premium", "five", "5"]) && plan.category === "signature") score += 5;
  if (chatContainsAny(text, ["three", "3", "advanced", "complete"]) && plan.category === "prime") score += 4;
  if (chatContainsAny(text, ["one", "1", "weekly", "starter", "beginner", "basic", "core"]) && plan.category === "core") score += 4;
  return score;
}

function findMatchingPlans(text) {
  const ranked = PLANS
    .map((plan) => ({ plan, score: planScore(plan, text) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score);
  return (ranked.length ? ranked.map((item) => item.plan) : PLANS).slice(0, 3);
}

function formatPlanReply(plans, intro = "Here are the best-fit Fitness Gurukul plans:") {
  const lines = [intro];
  plans.slice(0, 3).forEach((plan) => {
    lines.push(`${plan.name} - ${plan.price}, ${plan.sessions}. ${plan.summary} Key inclusions: ${plan.points.slice(0, 3).join(", ")}.`);
  });
  lines.push("For the exact fit, share your goal, schedule, location, and whether you prefer virtual or in-person coaching.");
  return lines.join(" ");
}

function compareCorePrimeSignatureReply() {
  const core = PLANS.find((plan) => plan.category === "core");
  const prime = PLANS.find((plan) => plan.category === "prime");
  const signature = PLANS.find((plan) => plan.category === "signature");
  return `${core.name} is the starter personalized plan: ${core.price} with ${core.sessions}. ${prime.name} is more hands-on: ${prime.price} with ${prime.sessions} and fuller fitness plus nutrition support. ${signature.name} is the intensive option: ${signature.price} with ${signature.sessions} for faster transformation, in-person PT, nutrition, posture assessment, and app check-ins.`;
}

function buildChatSystemPrompt() {
  const planLines = PLANS.map((plan) => `- ${plan.name} (${plan.price}, ${plan.sessions}): ${plan.summary} Highlights: ${plan.points.join(", ")}.`);
  return [
    "You are the Fitness Gurukul AI assistant for a premium fitness studio in Hyderabad, India.",
    "Behave like a helpful fitness consultant, not a scripted FAQ bot. Ask one useful follow-up question when the user's goal is vague.",
    "Recommend relevant website plans, services, coaches, or next steps. Never invent prices, coaches, dates, medical claims, or contact details.",
    "For medical, injury, pregnancy, or disease-related questions, give general fitness guidance only and recommend speaking with a qualified professional.",
    "Answer clearly, warmly, and concisely in 2-5 short sentences unless the user asks for detail.",
    "If unsure, invite the user to book a free consultation.",
    `Contact phone: ${CONTACT.phone}. WhatsApp: ${CONTACT.whatsapp}. Email: ${CONTACT.email}. Address: ${CONTACT.address}.`,
    "Current coaching plans from the website:",
    ...planLines,
  ].join("\n");
}

function extractOpenAIText(payload) {
  if (typeof payload.output_text === "string") return normalizeChatText(payload.output_text);
  const parts = [];
  (payload.output || []).forEach((item) => {
    (item.content || []).forEach((content) => {
      if (typeof content.text === "string") parts.push(content.text);
    });
  });
  return normalizeChatText(parts.join(" "));
}

function generateLocalChatReply(message) {
  const text = normalizeChatText(message).toLowerCase();
  if (!text) return "Ask me about training plans, coaches, pricing, events, or how to book a free consultation.";
  if (/^(hi|hello|hey|namaste)\b/.test(text)) {
    return "Hi! I am the Fitness Gurukul assistant. I can help with plans, coach matching, pricing, events, and booking a free consultation in Hyderabad.";
  }
  if (chatContainsAny(text, ["contact", "phone", "call", "whatsapp", "email", "address", "location", "where"])) {
    return `You can call ${CONTACT.phone}, WhatsApp ${CONTACT.whatsapp}, or email ${CONTACT.email}. Studio address: ${CONTACT.address}.`;
  }
  if (chatContainsAny(text, ["compare", "difference", "core", "prime", "signature"])) {
    return compareCorePrimeSignatureReply();
  }
  if (chatContainsAny(text, ["price", "cost", "fee", "how much", "pricing", "plan", "package", "program", "weight", "muscle", "hyrox", "running", "virtual", "online", "fitness", "strength", "transformation"])) {
    return formatPlanReply(findMatchingPlans(text));
  }
  if (chatContainsAny(text, ["doorstep", "home", "in person", "personal trainer"])) {
    return formatPlanReply(findMatchingPlans("in person personal training core prime signature"), "Yes. For in-person or doorstep-style coaching, these are the closest plan fits:");
  }
  if (chatContainsAny(text, ["yoga", "coach", "trainer", "instructor"])) {
    return "We have yoga, fitness, sports, kids, rehab, and special-needs coaches. For yoga, ask for Aditya Gururani, Nitu Arya, Rahul Bisht, Rahul Singh Pawar, or Parul Danu; for strength or weight loss, the team can match you after a free consultation.";
  }
  if (chatContainsAny(text, ["event", "marathon", "cycling", "ride", "camp", "born star", "obstacle"])) {
    return "Fitness Gurukul supports running events, cycling events, corporate wellness, group training, bootcamps, and community runs. Share the event type and team size to get a custom quote.";
  }
  return "I can help with Fitness Gurukul plans, coach recommendations, pricing, events, and booking. Try asking about weight loss, Core vs Prime, Signature, running, Hyrox, or virtual coaching.";
}

async function callOpenAIChat(message, history = []) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return null;
  const model = process.env.OPENAI_MODEL || "gpt-5.6";
  try {
    const input = [
      ...history.slice(-8).filter((item) => ["user", "assistant"].includes(item.role)).map((item) => ({ role: item.role, content: normalizeChatText(item.content) })),
      { role: "user", content: normalizeChatText(message) },
    ];
    const response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        instructions: buildChatSystemPrompt(),
        input,
        max_output_tokens: 450,
      }),
    });
    if (!response.ok) throw new Error(`OpenAI request failed: ${response.status}`);
    const payload = await response.json();
    return extractOpenAIText(payload);
  } catch (error) {
    console.warn("OpenAI chat error:", error.message);
    return null;
  }
}

// API: Submit form
app.get("/api/health", (req, res) => {
  res.json({ ok: true, engine: "node", aiEnabled: Boolean(process.env.OPENAI_API_KEY) });
});

app.get("/api/content", (req, res) => {
  res.json({ ok: true, plans: PLANS, contact: CONTACT });
});

app.get("/api/chat/status", (req, res) => {
  res.json({
    ok: true,
    aiEnabled: Boolean(process.env.OPENAI_API_KEY),
    engine: process.env.OPENAI_API_KEY ? "openai" : "local",
    model: process.env.OPENAI_MODEL || "gpt-5.6",
    suggestions: CHAT_SUGGESTIONS,
  });
});

app.post("/api/chat", async (req, res) => {
  const message = normalizeChatText(req.body.message);
  if (!message) return res.status(400).json({ ok: false, error: "Message is required" });
  if (message.length > 2000) return res.status(400).json({ ok: false, error: "Message is too long" });

  const history = Array.isArray(req.body.history) ? req.body.history : [];
  const aiReply = await callOpenAIChat(message, history);
  const source = aiReply ? "openai" : "local";
  const reply = aiReply || generateLocalChatReply(message);

  res.json({
    ok: true,
    reply,
    source,
    aiEnabled: source === "openai",
    suggestions: CHAT_SUGGESTIONS,
  });
});

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
