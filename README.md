# Fitness Gurukul Full-Stack Website

Multi-page Fitness Gurukul website with a responsive frontend, Python backend, and SQLite database.

## What is included

- Frontend: detailed pages in `public/`
- Backend: dependency-free Python HTTP API in `server.py`
- Database: SQLite file created automatically as `fitness_gurukul.sqlite3`
- Dashboard: view user-entered leads, progress check-ins, and newsletter entries
- Download: packaged project ZIP at `public/fitness-gurukul-fullstack.zip`

## Pages

- `index.html` - logo-led home, guide, featured services, story, events, testimonials
- `programs.html` - detailed services, filters, comparison table, packages
- `events.html` - corporate marathon, cycling, active day, and planning flow
- `community.html` - community runs, cycling crews, wellness challenges, and transformation paths
- `coaches.html` - coaches, specialties, standards, testimonials, updates
- `tools.html` - BMI, goal recommendation, check-ins, storage mode status
- `contact.html` - consultation form, contact cards, areas, FAQ, newsletter
- `owner-data.html` - direct owner-only data viewer, not linked in the client navigation

## Brand system

The UI uses the uploaded Fitness Gurukul logo colors only:

- Black/dark background
- Logo cyan and blue
- Fitness red
- White/ice text surfaces

The fonts are Montserrat for headings/buttons and Inter for body/UI text.

## Run locally

```bash
python server.py
```

Open:

```text
http://127.0.0.1:8000
```

To collect form data from another laptop on the same Wi-Fi, share your main laptop's network link:

```text
http://YOUR-LAPTOP-IP:8000/contact.html
```

Do not share `127.0.0.1` with another device. On another laptop, `127.0.0.1` points back to that other laptop.

## Where user data appears

Run the backend, submit a form, then open:

```text
http://127.0.0.1:8000/owner-data.html
```

The raw JSON is available at:

```text
http://127.0.0.1:8000/api/admin-data
```

Static hosting cannot run Python or SQLite, so static forms save demo records in the browser only.

## AI chatbot

The chatbot uses the server-side `/api/chat` endpoint. For real AI answers, create a `.env` file from `.env.example` and add your OpenAI API key:

```text
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-5.6
```

Then restart the server with `python server.py`. Without `OPENAI_API_KEY`, the chat widget still answers from website plan facts, but it runs in local fallback mode.

## API endpoints

- `GET /api/health`
- `GET /api/content`
- `GET /api/chat/status`
- `POST /api/chat`
- `POST /api/leads`
- `GET /api/leads`
- `POST /api/newsletter`
- `POST /api/checkins`
- `GET /api/stats`
- `GET /api/admin-data`
