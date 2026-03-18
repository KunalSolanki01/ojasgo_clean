# 🌿 OjasGo — Ayurvedic AI Sanctuary

> A full-stack Ayurvedic AI web application built with **Flask** + **Claude AI (Anthropic)**  
> Neumorphic design · 4-Pillar Protocol · 13 Ragas · Leela Board Game

---

## 📁 Project Structure

```
OjasGo/
│
├── app.py                  ← Flask backend (all routes + Ayurvedic engine)
├── requirements.txt        ← Python dependencies
├── .env.example            ← Environment variable template
│
├── templates/
│   └── index.html          ← Main Jinja2 template
│
└── static/
    ├── css/
    │   └── main.css        ← Complete neumorphic design system
    └── js/
        └── app.js          ← Frontend logic (API calls, UI, Leela game)
```

---

## 🚀 Quick Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure your API key
```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

Get your free API key at: **https://console.anthropic.com**

### 3. Run the Flask server
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes (for Claude AI) |
| `SECRET_KEY` | Flask session secret | Yes (change in production) |
| `FLASK_ENV` | `development` or `production` | Optional |

> **Note:** The app works WITHOUT a Claude API key using the built-in Ayurvedic keyword classifier as a fallback.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`               | Main application page |
| `POST` | `/api/chat`       | Claude AI consultation |
| `GET`  | `/api/data/ragas` | All 13 raga prescriptions |
| `GET`  | `/api/data/herbs` | Herbal pharmacopoeia |
| `GET`  | `/api/data/pranayamas` | Pranayama & mudra data |
| `GET`  | `/api/data/leela` | Leela board squares & names |
| `POST` | `/api/classify`   | Local dosha classifier |
| `GET`  | `/api/health`     | Server health + API status |

### `/api/chat` Request Body
```json
{
  "message": "I feel anxious and restless",
  "type": "vaidya"
}
```
`type` can be: `vaidya` | `raga` | `herb`

### `/api/chat` Response
```json
{
  "response": "🔮 PILLAR I — VIKALPA\n...",
  "source": "claude",
  "sattva": 10
}
```

---

## 🧠 Four-Pillar Protocol

```
User Input (free text)
        ↓
  [Vikalpa] — Dosha Classification (Claude AI)
  ↓
  [Raga] — Sound Therapy Prescription
  ↓
  [Dharana] — Herbs + Mudra + Pranayama
  ↓
  [Sadhana] — 21-Day Long-term Practice + Leela Game
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12 + Flask 3.x |
| AI | Claude AI (claude-sonnet-4-20250514) via Anthropic API |
| Frontend | Vanilla JS (ES6+) + HTML5 + CSS3 |
| Design | Neumorphic CSS design system |
| Fonts | Playfair Display + Inter + Cinzel |
| State | No framework — pure ES6 state object |
| Fallback | Built-in keyword dosha classifier (no API needed) |

---

## 🛡️ Disclaimer

All AI recommendations are for **educational and informational purposes only**.  
OjasGo does not dispense pharmaceutical prescriptions.  
Always consult a registered Vaidya or licensed healthcare professional.

---

*Built with 🌿 — Five thousand years of healing lineage, encoded for the modern age.*
