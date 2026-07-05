"""
Travel Day-Planner Agent
A real AI agent that builds a personalised one-day itinerary for any city.
Built with FastAPI + OpenAI. Serves a clean web UI at "/".
"""

import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Travel Day-Planner Agent")

# The OpenAI client reads OPENAI_API_KEY from the environment.
# Never hard-code the key — pass it in with `-e OPENAI_API_KEY=...`
client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class TripRequest(BaseModel):
    city: str
    interests: str = "general sightseeing"
    pace: str = "balanced"  # relaxed | balanced | packed


SYSTEM_PROMPT = """You are an expert local travel guide.
Build a single-day itinerary for the city the user gives you.
Tailor it to their interests and preferred pace.

Return ONLY valid JSON (no markdown, no backticks) in exactly this shape:
{
  "city": "City, Country",
  "summary": "One warm sentence about the day.",
  "stops": [
    {
      "time": "9:00 AM",
      "title": "Place or activity name",
      "description": "1-2 sentence why-you'll-love-it.",
      "tip": "One insider tip.",
      "emoji": "a single relevant emoji"
    }
  ]
}
Include 5 to 7 stops from morning to evening, including a lunch and a dinner stop.
Keep it realistic and geographically sensible."""


@app.get("/health")
def health():
    return {"status": "agent is live"}


@app.post("/plan")
def plan(req: TripRequest):
    user_msg = (
        f"City: {req.city}\n"
        f"Interests: {req.interests}\n"
        f"Pace: {req.pace}"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )
    itinerary = json.loads(resp.choices[0].message.content)
    return itinerary


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Travel Day-Planner Agent</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #0A1929 0%, #0D2438 100%);
    color: #e6f1ff; min-height: 100vh; padding: 24px;
  }
  .wrap { max-width: 720px; margin: 0 auto; }
  header { text-align: center; margin: 28px 0 32px; }
  h1 { font-size: 2rem; margin-bottom: 8px; }
  .sub { color: #7da2c9; font-size: 1rem; }
  .card {
    background: rgba(36, 150, 237, 0.08);
    border: 1px solid rgba(36, 150, 237, 0.25);
    border-radius: 16px; padding: 24px; margin-bottom: 20px;
  }
  label { display:block; font-size:.85rem; color:#9fc0e0; margin: 12px 0 6px; }
  input, select {
    width: 100%; padding: 12px 14px; border-radius: 10px;
    border: 1px solid rgba(36,150,237,.35); background:#0A1929;
    color:#e6f1ff; font-size:1rem;
  }
  input:focus, select:focus { outline:none; border-color:#2496ED; }
  button {
    width:100%; margin-top:20px; padding:14px; border:none; border-radius:10px;
    background: linear-gradient(135deg,#2496ED,#326CE5); color:white;
    font-size:1.05rem; font-weight:600; cursor:pointer; transition:.2s;
  }
  button:hover { transform: translateY(-1px); opacity:.95; }
  button:disabled { opacity:.5; cursor:not-allowed; transform:none; }
  .summary { color:#9fc0e0; font-style:italic; margin: 8px 0 20px; text-align:center; }
  .stop {
    display:flex; gap:14px; padding:16px 0;
    border-top:1px solid rgba(36,150,237,.15);
  }
  .stop:first-child { border-top:none; }
  .emoji { font-size:1.8rem; flex-shrink:0; }
  .time { color:#2496ED; font-weight:700; font-size:.85rem; }
  .title { font-size:1.1rem; font-weight:600; margin:2px 0 4px; }
  .desc { color:#c3d9f0; font-size:.92rem; line-height:1.5; }
  .tip { color:#7da2c9; font-size:.85rem; margin-top:6px; }
  .tip b { color:#9fc0e0; }
  .loading { text-align:center; color:#7da2c9; padding:20px; }
  .hidden { display:none; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🌍 Travel Day-Planner</h1>
    <div class="sub">Tell me a city — I'll plan your perfect day.</div>
  </header>

  <div class="card">
    <label>Where are you going?</label>
    <input id="city" placeholder="e.g. Kyoto, Lisbon, Jaipur..." />

    <label>What are you into?</label>
    <input id="interests" placeholder="e.g. history, street food, art" value="history and local food" />

    <label>Pace</label>
    <select id="pace">
      <option value="relaxed">Relaxed</option>
      <option value="balanced" selected>Balanced</option>
      <option value="packed">Packed</option>
    </select>

    <button id="go" onclick="plan()">Plan my day ✨</button>
  </div>

  <div id="result"></div>
</div>

<script>
async function plan() {
  const city = document.getElementById('city').value.trim();
  if (!city) { alert('Please enter a city!'); return; }
  const btn = document.getElementById('go');
  const result = document.getElementById('result');
  btn.disabled = true; btn.textContent = 'Planning...';
  result.innerHTML = '<div class="loading">🧭 Building your itinerary...</div>';

  try {
    const res = await fetch('/plan', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        city: city,
        interests: document.getElementById('interests').value,
        pace: document.getElementById('pace').value
      })
    });
    const data = await res.json();
    let html = '<div class="card"><h2>'+data.city+'</h2>';
    html += '<div class="summary">'+data.summary+'</div>';
    for (const s of data.stops) {
      html += '<div class="stop"><div class="emoji">'+(s.emoji||'📍')+'</div><div>';
      html += '<div class="time">'+s.time+'</div>';
      html += '<div class="title">'+s.title+'</div>';
      html += '<div class="desc">'+s.description+'</div>';
      if (s.tip) html += '<div class="tip"><b>Tip:</b> '+s.tip+'</div>';
      html += '</div></div>';
    }
    html += '</div>';
    result.innerHTML = html;
  } catch (e) {
    result.innerHTML = '<div class="card">Something went wrong. Check the server logs.</div>';
  } finally {
    btn.disabled = false; btn.textContent = 'Plan my day ✨';
  }
}
</script>
</body>
</html>"""
