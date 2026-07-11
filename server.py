from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from urllib import request as urlrequest
import json
import os
import re
import socket
import sqlite3
import time

ROOT = Path(__file__).parent.resolve()
PUBLIC = ROOT
DB_PATH = ROOT / "fitness_gurukul.sqlite3"
DB_SCHEMA_READY = False

CONTACT = {
    "phone": "08042781491",
    "whatsapp": "+917207113310",
    "email": "contact@fitnessgurukul.co.in",
    "address": "H.no.1-10/2, Lakshmi Nagar Colony, near Pochamma Temple, Manikonda, Hyderabad, 500089",
    "city": "Hyderabad, India",
}

SERVICES = [
    {"name": "Personal Training", "tag": "Gym, Sports, Strength, Cross Fit", "category": "training", "summary": "FREE demo session with our Personal Trainers. Book today and get a healthy discount!", "price": "Free demo", "accent": "blue", "points": ["Strength training", "Cross fit", "Sports conditioning", "Weight management"]},
    {"name": "Personalised Doorstep Service", "tag": "Home coaching", "category": "training", "summary": "Doorstep service for strength training, weight loss, body toning, stress relief. Helping people LIVE their best life!", "price": "Custom quote", "accent": "cyan", "points": ["Home training", "Weight loss", "Body toning", "Stress relief"]},
    {"name": "Yogic Wellness", "tag": "Yoga & flexibility", "category": "recovery", "summary": "Hatha yoga, corporate yoga, personal yoga training. Free demo session for your yogic transformation.", "price": "Free demo", "accent": "red", "points": ["Hatha yoga", "Flexibility", "Weight loss", "Corporate yoga"]},
    {"name": "Swimming", "tag": "Technique & confidence", "category": "training", "summary": "Water confidence, breathing rhythm, stroke correction, endurance. Safe, guided sessions.", "price": "Custom quote", "accent": "cyan", "points": ["Breathing rhythm", "Stroke basics", "Endurance", "Water confidence"]},
    {"name": "Weight Loss & Diet Plan", "tag": "Nutrition coaching", "category": "nutrition", "summary": "Diet consultation for a balanced and healthy life. One week free demo diet plan available.", "price": "Free demo", "accent": "red", "points": ["Diet consultation", "Custom meal plan", "Balanced nutrition", "Healthy lifestyle"]},
    {"name": "Corporate Marathon Events & Management", "tag": "Running events", "category": "event", "summary": "The Race Ends At Finish Line, But The Memories Last Forever! Promoting healthy & active lifestyles.", "price": "Custom quote", "accent": "blue", "points": ["Marathon management", "Participant comms", "Route support", "Race-day energy"]},
    {"name": "Corporate Cycling Events", "tag": "Cycling adventures", "category": "event", "summary": "Active, engaging & fun one day events or multi-day tours. Build camaraderie and promote fitness.", "price": "Custom quote", "accent": "cyan", "points": ["Team bonding", "Route planning", "Safety support", "Recovery"]},
    {"name": "Kids Programs", "tag": "Age 5-12", "category": "training", "summary": "Nature-inspired yoga, animal kingdom workouts, core and lower body strengthening for kids.", "price": "From INR 3,000", "accent": "blue", "points": ["Kids fitness", "Sports skills", "Coordination", "Confidence"]},
    {"name": "TTC Certification Courses", "tag": "Teacher training", "category": "training", "summary": "200 hours TTC in Yoga and Yogic Aahaar nutrition certification.", "price": "Custom quote", "accent": "cyan", "points": ["200 hour TTC", "Yoga certification", "Nutrition course", "Teaching practice"]},
    {"name": "Group Training", "tag": "Community", "category": "event", "summary": "Sports events, recreational activities, meet events, bootcamps. Group motivation.", "price": "Batch based", "accent": "blue", "points": ["Group sessions", "Sports events", "Bootcamps", "Community"]},
    {"name": "Corporate Services", "tag": "Office wellness", "category": "event", "summary": "Office yoga, fun activities, mini shows, games and sports for corporate teams.", "price": "Custom quote", "accent": "cyan", "points": ["Office yoga", "Team activities", "Games", "Event planning"]},
    {"name": "Fitness Gurukul Born Star Running Event", "tag": "Community run", "category": "event", "summary": "Community-focused running event. INR 900 - INR 1000. For beginners and regular runners.", "price": "INR 900", "accent": "red", "points": ["Community run", "Beginner friendly", "Race experience", "Finisher medal"]},
]

COACHES = [
    {"name": "Aditya Gururani", "role": "Yoga Instructor & Breathing Specialist", "slug": "aditya-gururani", "category": "yoga", "bio": "A certified yoga instructor specializing in breathwork, stress management, and functional mobility. Focused on helping individuals improve posture, flexibility, lung capacity, and mental clarity through structured yoga and scientifically grounded breathing techniques.", "focus": ["Breathwork", "Stress management", "Functional mobility"]},
    {"name": "B Yashwanth", "role": "Basketball Coach", "slug": "b-yashwanth", "category": "sports", "bio": "Basketball Coach", "focus": ["Basketball", "Sports coaching", "Conditioning"]},
    {"name": "Kritika Chauhan", "role": "Yoga Instructor", "slug": "kritika-chauhan", "category": "yoga", "bio": "Yoga Instructor", "focus": ["Yoga", "Flexibility", "Mobility"]},
    {"name": "Shivajeet Kanaujiya", "role": "Fitness Trainer", "slug": "shivajeet-kanaujiya", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Daily exercise"]},
    {"name": "Anand Yadav", "role": "Children’s Athletics Coach", "slug": "anand-yadav", "category": "kids", "bio": "Children’s Athletics Coach", "focus": ["Children's athletics", "Kids fitness", "Sports"]},
    {"name": "Chandan Mondal", "role": "Bodybuilding & Fitness Coach", "slug": "chandan-mondal", "category": "fitness", "bio": "Bodybuilding & Fitness Coach", "focus": ["Bodybuilding", "Fitness", "Strength"]},
    {"name": "Aditya", "role": "Yoga Instructor & Fitness Coach", "slug": "aditya", "category": "yoga", "bio": "Yoga Instructor & Fitness Coach", "focus": ["Yoga", "Fitness", "Body toning"]},
    {"name": "Nitu Arya", "role": "Yoga Instructor", "slug": "nitu-arya", "category": "yoga", "bio": "Yoga Instructor", "focus": ["Yoga", "Flexibility", "General fitness"]},
    {"name": "Rahul Bisht", "role": "Yoga Instructor", "slug": "rahul-bisht", "category": "yoga", "bio": "Yoga Instructor", "focus": ["Yoga", "Mobility", "General fitness"]},
    {"name": "Deepesh Kumar", "role": "Fitness Trainer", "slug": "deepesh-kumar", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Weight loss"]},
    {"name": "S Jeetender", "role": "Fitness Trainer", "slug": "s-jeetender", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Daily exercise", "Strength"]},
    {"name": "Rahul Dawar", "role": "Fitness Trainer", "slug": "rahul-dawar", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Health routine"]},
    {"name": "Rahul Singh Pawar", "role": "Yoga Instructor", "slug": "rahul-singh-pawar", "category": "yoga", "bio": "Yoga Instructor", "focus": ["Yoga", "Flexibility", "Stress relief"]},
    {"name": "Ravi Pal", "role": "Fitness Trainer & Injury Rehabilitation Coach", "slug": "ravi-pal", "category": "rehab", "bio": "Fitness Trainer & Injury Rehabilitation Coach", "focus": ["Fitness training", "Injury rehabilitation", "Recovery"]},
    {"name": "Subedhar Yadav", "role": "Fitness Trainer (Special Children)", "slug": "subedhar-yadav", "category": "special", "bio": "Fitness Trainer (Special Children)", "focus": ["Special children", "Fitness", "Mobility"]},
    {"name": "Sanjeev", "role": "Fitness Trainer", "slug": "sanjeev", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Daily exercise"]},
    {"name": "Nandlal", "role": "Fitness Trainer", "slug": "nandlal", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Weight loss"]},
    {"name": "Prasenjit Ghosh", "role": "Mudgar & Hybrid Training Specialist", "slug": "prasenjit-ghosh", "category": "hybrid", "bio": "Mudgar & Hybrid Training Specialist", "focus": ["Mudgar", "Hybrid training", "Strength"]},
    {"name": "Vinay Ojha", "role": "Fitness Trainer", "slug": "vinay-ojha", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "General fitness"]},
    {"name": "Ankit Singh Chauhan", "role": "Fitness & Calisthenics Trainer", "slug": "ankit-singh-chauhan", "category": "fitness", "bio": "Fitness & Calisthenics Trainer", "focus": ["Fitness", "Calisthenics", "Strength"]},
    {"name": "Suresh Yadav", "role": "Fitness Trainer (Special Children)", "slug": "suresh-yadav", "category": "special", "bio": "Fitness Trainer (Special Children)", "focus": ["Special children", "Fitness", "Mobility"]},
    {"name": "Parul Danu", "role": "Yoga Instructor", "slug": "parul-danu", "category": "yoga", "bio": "Yoga Instructor", "focus": ["Yoga", "Flexibility", "Stress relief"]},
    {"name": "Raju", "role": "Fitness Trainer", "slug": "raju", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Health routine"]},
    {"name": "Vishal Choudhary", "role": "Fitness Trainer", "slug": "vishal-choudhary", "category": "fitness", "bio": "Fitness Trainer", "focus": ["Fitness training", "Strength", "Personal training"]},
]

TESTIMONIALS = [
    {"name": "Priyanka", "quote": "Rohit, ur training are excellent. I can feel the difference every week, with my stamina and strength improving.", "result": "Strength & stamina"},
    {"name": "Lakshman, Sridhar & Rahul", "quote": "Thank you Shiv Narayan for your coaching, the sand exercises really pushed us to our limits.", "result": "Running prep"},
    {"name": "Undisclosed", "quote": "Vishal sir has helped me a lot in my fitness journey, its been a while that I have been training.", "result": "Personal training"},
]

UPDATES = [
    {"title": "Online Personal Trainer in Hyderabad – Flexible Coaching for Modern Lifestyles", "date": "2026-02-17", "summary": "Flexible coaching with check-ins, workouts, and nutrition support for modern schedules."},
    {"title": "Certified Personal Trainer in Hyderabad – Qualified Guidance You Can Trust", "date": "2026-02-14", "summary": "Qualified programming helps clients train safely, recover better, and build repeatable habits."},
    {"title": "Best Dietician for Weight Loss in Hyderabad – Practical Nutrition for Real Change", "date": "2026-02-14", "summary": "Food choices, portions, and routine design for sustainable weight management."},
]

SERVICE_AREAS = ["Manikonda", "Lakshmi Nagar Colony", "Puppalaguda", "Shaikpet", "Gachibowli", "Kokapet", "Narsingi", "Financial District", "HITEC City", "Madhapur", "Jubilee Hills"]

CHAT_SUGGESTIONS = [
    "What programs do you offer?",
    "How much does personal training cost?",
    "Do you offer doorstep coaching?",
    "Which coach is best for yoga?",
]

def content_payload():
    return {
        "services": SERVICES,
        "coaches": COACHES,
        "testimonials": TESTIMONIALS,
        "updates": UPDATES,
        "serviceAreas": SERVICE_AREAS,
        "contact": CONTACT,
    }

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    global DB_SCHEMA_READY
    with get_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL, goal TEXT NOT NULL, program TEXT NOT NULL, message TEXT, created_at INTEGER NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS newsletter (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, created_at INTEGER NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, weight REAL NOT NULL, stamina INTEGER NOT NULL, mood TEXT NOT NULL, created_at INTEGER NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS ai_scans (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, focus TEXT NOT NULL, summary TEXT NOT NULL, coach_route TEXT NOT NULL, camera_used INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS calculator_results (id INTEGER PRIMARY KEY AUTOINCREMENT, calculator TEXT NOT NULL, title TEXT NOT NULL, result TEXT NOT NULL, unit TEXT, rating TEXT, created_at INTEGER NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS chat_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'local', created_at INTEGER NOT NULL)")
        conn.commit()
    DB_SCHEMA_READY = True

def build_chat_system_prompt():
    service_lines = []
    for service in SERVICES:
        points = ", ".join(service.get("points", [])[:4])
        service_lines.append(f"- {service['name']} ({service['price']}): {service['summary']} Highlights: {points}.")
    coach_lines = []
    for coach in COACHES[:12]:
        focus = ", ".join(coach.get("focus", [])[:3])
        coach_lines.append(f"- {coach['name']}, {coach['role']}. Focus: {focus}.")
    return (
        "You are the Fitness Gurukul AI assistant for a premium fitness studio in Hyderabad, India. "
        "Answer clearly, warmly, and concisely in 2-5 short sentences unless the user asks for detail. "
        "Recommend relevant services, coaches, or next steps. Never invent prices, coaches, or contact details. "
        "If unsure, invite the user to book a free consultation.\n\n"
        f"Contact phone: {CONTACT['phone']}. WhatsApp: {CONTACT['whatsapp']}. Email: {CONTACT['email']}. "
        f"Address: {CONTACT['address']}. Service areas: {', '.join(SERVICE_AREAS[:8])}.\n\n"
        "Services:\n" + "\n".join(service_lines) + "\n\n"
        "Sample coaches:\n" + "\n".join(coach_lines)
    )

def normalize_chat_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip())

def chat_contains_any(text, words):
    return any(word in text for word in words)

def find_matching_coaches(text):
    matches = []
    for coach in COACHES:
        haystack = " ".join([
            coach.get("name", ""),
            coach.get("role", ""),
            coach.get("category", ""),
            " ".join(coach.get("focus", [])),
            coach.get("bio", ""),
        ]).lower()
        if any(token in haystack for token in text.split() if len(token) > 3):
            matches.append(coach)
    if matches:
        return matches[:3]
    if chat_contains_any(text, ["yoga", "breath", "flexibility", "stress"]):
        return [coach for coach in COACHES if coach.get("category") == "yoga"][:3]
    if chat_contains_any(text, ["kid", "child", "children"]):
        return [coach for coach in COACHES if coach.get("category") in {"kids", "special"}][:3]
    if chat_contains_any(text, ["injury", "rehab", "recovery"]):
        return [coach for coach in COACHES if coach.get("category") == "rehab"][:3]
    if chat_contains_any(text, ["sport", "basketball", "running", "calisthenics"]):
        return [coach for coach in COACHES if coach.get("category") in {"sports", "fitness", "hybrid"}][:3]
    return []

def find_matching_services(text):
    matches = []
    for service in SERVICES:
        haystack = " ".join([
            service.get("name", ""),
            service.get("tag", ""),
            service.get("category", ""),
            service.get("summary", ""),
            " ".join(service.get("points", [])),
        ]).lower()
        if any(token in haystack for token in text.split() if len(token) > 3):
            matches.append(service)
    if matches:
        return matches[:3]
    keyword_map = [
        (["yoga", "breath", "flexibility", "wellness"], ["Yogic Wellness"]),
        (["doorstep", "home", "at home"], ["Personalised Doorstep Service"]),
        (["weight", "fat", "diet", "nutrition"], ["Weight Loss & Diet Plan", "Personal Training"]),
        (["swim", "pool", "water"], ["Swimming"]),
        (["kid", "child", "children"], ["Kids Programs"]),
        (["corporate", "office", "team"], ["Corporate Services", "Corporate Marathon Events & Management"]),
        (["run", "marathon", "race"], ["Corporate Marathon Events & Management", "Fitness Gurukul Born Star Running Event"]),
        (["cycl", "bike", "ride"], ["Corporate Cycling Events"]),
        (["group", "bootcamp", "community"], ["Group Training", "Fitness Gurukul Born Star Running Event"]),
    ]
    for keywords, names in keyword_map:
        if chat_contains_any(text, keywords):
            return [service for service in SERVICES if service["name"] in names][:3]
    return SERVICES[:3]

def format_service_reply(services):
    lines = ["Here are the best-fit options I found:"]
    for service in services:
        lines.append(f"• {service['name']} — {service['price']}. {service['summary']}")
    lines.append("Want a free consultation? Visit the Contact page or WhatsApp us at +91 72071 13310.")
    return " ".join(lines)

def format_coach_reply(coaches):
    if not coaches:
        return (
            "We have 24 expert coaches across yoga, strength, sports, kids fitness, rehab, and special-needs training. "
            "Browse coaches.html or tell me your goal and I will narrow it down."
        )
    lines = ["These coaches look like a strong match:"]
    for coach in coaches:
        focus = ", ".join(coach.get("focus", [])[:3])
        lines.append(f"• {coach['name']} — {coach['role']}. Focus: {focus}.")
    lines.append("You can view full profiles on the Coaches page or book a call to get matched faster.")
    return " ".join(lines)

def generate_local_chat_reply(message, history=None):
    text = normalize_chat_text(message).lower()
    if not text:
        return "Ask me about training plans, coaches, pricing, events, or how to book a free consultation."

    greetings = ["hi", "hello", "hey", "good morning", "good evening", "namaste"]
    if text in greetings or any(text.startswith(g + " ") or text == g for g in greetings):
        return (
            "Hi! I am the Fitness Gurukul assistant. I can help with programs, coach matching, "
            "pricing, events, and booking a free consultation in Hyderabad."
        )

    if chat_contains_any(text, ["thank", "thanks", "thank you"]):
        return "Happy to help. If you want to take the next step, book a free consultation on the Contact page."

    if chat_contains_any(text, ["contact", "phone", "call", "whatsapp", "email", "address", "location", "where"]):
        return (
            f"You can reach us at {CONTACT['phone']} or WhatsApp {CONTACT['whatsapp']}. "
            f"Email: {CONTACT['email']}. Studio address: {CONTACT['address']}."
        )

    if chat_contains_any(text, ["price", "cost", "fee", "how much", "pricing", "plan", "package"]):
        priced = [f"{service['name']} ({service['price']})" for service in SERVICES[:6]]
        return (
            "Pricing depends on the program. Popular options include "
            + "; ".join(priced)
            + ". Many services include a free demo. Book a consultation for an exact quote."
        )

    if chat_contains_any(text, ["coach", "trainer", "instructor", "who should", "recommend"]):
        return format_coach_reply(find_matching_coaches(text))

    if chat_contains_any(text, ["event", "marathon", "cycling", "ride", "camp", "born star", "obstacle"]):
        events = [service for service in SERVICES if service.get("category") == "event"]
        return format_service_reply(events[:4] if events else SERVICES[:3])

    if chat_contains_any(text, ["demo", "trial", "consultation", "book", "join", "start", "signup", "sign up"]):
        return (
            "Great next step: book a free consultation on contact.html. Share your goal, schedule, and area "
            "and we will match you with the right coach or program."
        )

    if chat_contains_any(text, ["service", "program", "offer", "training", "personal", "doorstep", "yoga", "swim", "weight", "diet", "kids", "corporate"]):
        return format_service_reply(find_matching_services(text))

    if chat_contains_any(text, ["area", "manikonda", "gachibowli", "hyderabad", "near", "local"]):
        return (
            "We serve Hyderabad including "
            + ", ".join(SERVICE_AREAS[:6])
            + ". Doorstep coaching availability depends on your exact location and preferred time."
        )

    if chat_contains_any(text, ["app", "download", "android", "iphone", "ios"]):
        return (
            "Download the Fitness Gurukul app on Google Play or the App Store to track workouts, book sessions, "
            "and stay connected with your coach."
        )

    return (
        "I can help with Fitness Gurukul programs, coach recommendations, pricing, events, and booking. "
        "Try asking about personal training, yoga, weight loss, doorstep coaching, or upcoming events."
    )

def call_openai_chat(message, history=None):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    messages = [{"role": "system", "content": build_chat_system_prompt()}]
    for item in (history or [])[-8:]:
        role = str(item.get("role", "")).strip()
        content = normalize_chat_text(item.get("content", ""))
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": normalize_chat_text(message)})
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 350,
    }).encode("utf-8")
    req = urlrequest.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=25) as res:
            body = json.loads(res.read().decode("utf-8"))
        choices = body.get("choices") or []
        if not choices:
            return None
        return normalize_chat_text(((choices[0].get("message") or {}).get("content")))
    except Exception as exc:
        print("OpenAI chat error:", exc)
        return None

def generate_chat_reply(message, history=None):
    ai_reply = call_openai_chat(message, history)
    if ai_reply:
        return ai_reply, "openai"
    return generate_local_chat_reply(message, history), "local"

def save_chat_exchange(session_id, user_message, assistant_message, source):
    sid = normalize_chat_text(session_id) or "anonymous"
    now = int(time.time())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content, source, created_at) VALUES (?, ?, ?, ?, ?)",
            (sid, "user", normalize_chat_text(user_message), source, now),
        )
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content, source, created_at) VALUES (?, ?, ?, ?, ?)",
            (sid, "assistant", normalize_chat_text(assistant_message), source, now),
        )
        conn.commit()

def ensure_database():
    if not DB_SCHEMA_READY or not DB_PATH.exists():
        init_db()

class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC), **kwargs)

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        ensure_database()
        path = urlparse(self.path).path
        if path.endswith(".sqlite3"):
            return self.send_json({"error": "Not found"}, 404)
        if path == "/api/health":
            with get_connection() as conn:
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            return self.send_json({"ok": True, "database": str(DB_PATH), "databaseExists": DB_PATH.exists(), "tables": [row["name"] for row in tables]})
        if path == "/api/content":
            return self.send_json(content_payload())
        if path == "/api/chat/status":
            has_openai = bool(os.environ.get("OPENAI_API_KEY", "").strip())
            return self.send_json({
                "ok": True,
                "aiEnabled": has_openai,
                "engine": "openai" if has_openai else "local",
                "suggestions": CHAT_SUGGESTIONS,
            })
        if path == "/api/admin-data":
            with get_connection() as conn:
                leads = conn.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 50").fetchall()
                checkins = conn.execute("SELECT * FROM checkins ORDER BY created_at DESC LIMIT 50").fetchall()
                newsletter = conn.execute("SELECT * FROM newsletter ORDER BY created_at DESC LIMIT 50").fetchall()
                ai_scans = conn.execute("SELECT * FROM ai_scans ORDER BY created_at DESC LIMIT 50").fetchall()
                calculations = conn.execute("SELECT * FROM calculator_results ORDER BY created_at DESC LIMIT 50").fetchall()
                chat_messages = conn.execute("SELECT * FROM chat_messages ORDER BY created_at DESC LIMIT 50").fetchall()
            return self.send_json({"leads": [dict(r) for r in leads], "checkins": [dict(r) for r in checkins], "newsletter": [dict(r) for r in newsletter], "ai_scans": [dict(r) for r in ai_scans], "calculations": [dict(r) for r in calculations], "chat_messages": [dict(r) for r in chat_messages]})
        if not (PUBLIC / path.lstrip("/")).exists() and path != "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        ensure_database()
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
        except json.JSONDecodeError:
            return self.send_json({"error": "Invalid JSON"}, 400)
        if path == "/api/leads":
            required = ["name", "phone", "goal", "program"]
            missing = [f for f in required if not str(payload.get(f, "")).strip()]
            if missing:
                return self.send_json({"error": "Missing required fields", "fields": missing}, 400)
            with get_connection() as conn:
                conn.execute("INSERT INTO leads (name, phone, goal, program, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (str(payload["name"]).strip(), str(payload["phone"]).strip(), str(payload["goal"]).strip(), str(payload["program"]).strip(), str(payload.get("message", "")).strip(), int(time.time())))
                conn.commit()
            return self.send_json({"ok": True, "message": "Saved."}, 201)
        if path == "/api/calculations":
            required = ["calculator", "title", "result"]
            missing = [f for f in required if not str(payload.get(f, "")).strip()]
            if missing:
                return self.send_json({"error": "Missing required fields", "fields": missing}, 400)
            with get_connection() as conn:
                conn.execute("INSERT INTO calculator_results (calculator, title, result, unit, rating, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (str(payload["calculator"]).strip(), str(payload["title"]).strip(), str(payload["result"]).strip(), str(payload.get("unit", "")).strip(), str(payload.get("rating", "")).strip(), int(time.time())))
                conn.commit()
            return self.send_json({"ok": True, "message": "Saved."}, 201)
        if path == "/api/chat":
            message = normalize_chat_text(payload.get("message", ""))
            if not message:
                return self.send_json({"error": "Message is required"}, 400)
            if len(message) > 2000:
                return self.send_json({"error": "Message is too long"}, 400)
            history = payload.get("history") if isinstance(payload.get("history"), list) else []
            session_id = normalize_chat_text(payload.get("sessionId", "")) or "anonymous"
            reply, source = generate_chat_reply(message, history)
            try:
                save_chat_exchange(session_id, message, reply, source)
            except Exception as exc:
                print("Chat save error:", exc)
            return self.send_json({
                "ok": True,
                "reply": reply,
                "source": source,
                "suggestions": CHAT_SUGGESTIONS,
            })
        return self.send_json({"error": "Not found"}, 404)

if __name__ == "__main__":
    init_db()
    host = "0.0.0.0"
    port = 8000
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        local_ip = "YOUR-LAPTOP-IP"
    server = ThreadingHTTPServer((host, port), AppHandler)
    print("Fitness Gurukul running at http://127.0.0.1:8000")
    print(f"Share on Wi-Fi: http://{local_ip}:8000")
    server.serve_forever()
