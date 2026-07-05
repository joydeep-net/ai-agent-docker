# 🌍 Travel Day-Planner Agent

A real AI agent that builds a personalised one-day itinerary for any city.
Built with **FastAPI + OpenAI**, packaged with **Docker**. Perfect for a live demo.

Type a city, pick your interests and pace, and the agent returns a warm,
emoji-tagged, morning-to-evening plan — served through a clean web UI.

---

## What's inside

| File | Purpose |
|------|---------|
| `app.py` | The agent + web UI (FastAPI) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Recipe to build the image |
| `docker-compose.yml` | One-command deploy (Method 2) |
| `.env.example` | Shows which env var to set |
| `.dockerignore` | Keeps the image clean |

---

## Run it locally (before Docker)

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-your-key
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

---

## Method 1 — `docker run`

```bash
# Build
docker build -t travel-agent .

# Run
docker run -d -p 80:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  --restart unless-stopped \
  --name travel-agent \
  travel-agent
```

Open http://localhost  (or http://<server-ip>/ on Vultr)

---

## Push to Docker Hub (so the server can pull it)

```bash
docker tag travel-agent yourusername/travel-agent
docker login
docker push yourusername/travel-agent
```

On the Vultr server:

```bash
docker pull yourusername/travel-agent
docker run -d -p 80:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  --restart unless-stopped \
  yourusername/travel-agent
```

---

## Method 2 — `docker compose`

Set your key first, then one command:

```bash
export OPENAI_API_KEY=sk-your-key
docker compose up -d
docker compose logs -f
```

Stop everything:

```bash
docker compose down
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web UI |
| GET | `/health` | Returns `{"status": "agent is live"}` |
| POST | `/plan` | JSON in → itinerary JSON out |

Test the API directly:

```bash
curl -X POST http://localhost/plan \
  -H "Content-Type: application/json" \
  -d '{"city": "Jaipur", "interests": "history and street food", "pace": "balanced"}'
```

---

## Notes for the talk

- Replace `yourusername` with your Docker Hub username everywhere.
- Never put your real key on a slide — pass it with `-e` on the server only.
- Default model is `gpt-4o-mini` (fast + cheap). Override with `OPENAI_MODEL`.
