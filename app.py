"""
OjasGo — Ayurvedic AI Sanctuary
Flask Backend Application
"""

import os
import json
import re
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import urllib.request
import urllib.error

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ojasgo-secret-2026-ayurveda")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ─────────────────────────────────────────────
# AYURVEDIC KNOWLEDGE BASE
# ─────────────────────────────────────────────

RAGAS = [
    {"id": 1,  "name": "Ahir Bhairav",    "time": "Early Morning", "dosha": "Kapha",       "chakra": "Crown",       "level": "Mild",         "effect": "Soothing serene alertness; calms Kapha sluggishness at dawn"},
    {"id": 2,  "name": "Hamsadhwani",     "time": "Morning",       "dosha": "Vata",        "chakra": "Throat",      "level": "Mild",         "effect": "Clears the mind; sharpens focus and mental concentration"},
    {"id": 3,  "name": "Bilahari",        "time": "Morning",       "dosha": "Pitta",       "chakra": "Heart",       "level": "Moderate",     "effect": "Joyous uplift; elevates mood and reduces morning fatigue"},
    {"id": 4,  "name": "Sama",            "time": "Morning",       "dosha": "Vata",        "chakra": "Ajna",        "level": "Mild–Moderate","effect": "Deeply calming; reduces anxiety; restores inner equilibrium"},
    {"id": 5,  "name": "Mohanam",         "time": "Morning/Eve",   "dosha": "Vata",        "chakra": "Throat",      "level": "Mild",         "effect": "Positive energy; reduces overthinking; cultivates clarity"},
    {"id": 6,  "name": "Bhimpalas",       "time": "Midday",        "dosha": "Pitta",       "chakra": "Solar Plexus","level": "Moderate",     "effect": "Encourages productivity; midday focus and emotional balance"},
    {"id": 7,  "name": "Yaman",           "time": "Evening",       "dosha": "Vata",        "chakra": "Sacral",      "level": "Moderate",     "effect": "Peaceful settlement; purifies emotions; promotes inner joy"},
    {"id": 8,  "name": "Kalyani",         "time": "Evening",       "dosha": "Vata",        "chakra": "Crown",       "level": "Moderate",     "effect": "Stabilizes mood; emotional rebalancing; deep inner calm"},
    {"id": 9,  "name": "Puriya",          "time": "Evening",       "dosha": "Pitta",       "chakra": "Ajna",        "level": "High",         "effect": "Clinically proven anxiety reduction (p=0.018) — RCT validated"},
    {"id": 10, "name": "Darbari Kanada",  "time": "Late Night",    "dosha": "All Doshas",  "chakra": "Ajna",        "level": "Panic/Crisis", "effect": "Deep tension relief; profound grounding; eases the overloaded mind"},
    {"id": 11, "name": "Malkauns",        "time": "Late Night",    "dosha": "Kapha",       "chakra": "Root",        "level": "High",         "effect": "Measurably lowers cortisol; deep calm; profound stress relief"},
    {"id": 12, "name": "Bageshri",        "time": "Night",         "dosha": "Pitta",       "chakra": "Ajna",        "level": "High",         "effect": "Soothes acute anxiety; aids hypertension; emotional stability"},
    {"id": 13, "name": "Nilambari",       "time": "Night",         "dosha": "Kapha",       "chakra": "Crown",       "level": "Insomnia",     "effect": "Induces deep restful sleep; calms the overactive Kapha mind"},
]

HERBS = [
    {"emoji": "🌿", "name": "Ashwagandha",  "sanskrit": "Withania somnifera",       "dosha": "Vata",       "tag": "Adaptogen",   "body": "Meta-analysis confirmed: lowers anxiety vs. placebo. Supreme Vata rasayana. Warm milk at night. (PubMed 36017529)"},
    {"emoji": "🍃", "name": "Brahmi",        "sanskrit": "Bacopa monnieri",          "dosha": "Pitta",      "tag": "Nootropic",   "body": "Mood-stabilising; reduces Pitta anxiety; memory-enhancing neuroprotective. (Scientific Reports RCT)"},
    {"emoji": "🌸", "name": "Jatamansi",     "sanskrit": "Nardostachys jatamansi",   "dosha": "Kapha",      "tag": "Nervine",     "body": "RCT vs. Imipramine: proven anxiolytic in Generalised Anxiety Disorder. Himalayan nervine tonic."},
    {"emoji": "🌱", "name": "Tulsi",         "sanskrit": "Ocimum sanctum",           "dosha": "All Doshas", "tag": "Immunomodulator", "body": "Adaptogenic; reduces cortisol; anti-inflammatory. Sacred Pitta-pacifying immunomodulator. Daily tea."},
    {"emoji": "🌾", "name": "Shatavari",     "sanskrit": "Asparagus racemosus",      "dosha": "Vata+Pitta", "tag": "Rejuvenative","body": "Supports HPA axis regulation; reduces stress-related fatigue. Supreme Vata and Pitta rejuvenative."},
]

PRANAYAMAS = [
    {"icon": "🌬", "name": "Nadi-Shodhana", "dosha": "Vata",       "body": "Alternate nostril; 4-count inhale, hold, 8-count exhale. Balances hemispheres; normalises HRV; calms anxiety."},
    {"icon": "💨", "name": "Bhramari",       "dosha": "Pitta/Vata", "body": "Humming exhalation with closed eyes. Immediate parasympathetic dominance; reduces cortisol acutely."},
    {"icon": "🔥", "name": "Bhastrika",      "dosha": "Kapha",      "body": "Vigorous bellows breath. fMRI confirmed: lowers anxiety; improves brain connectivity and energy."},
    {"icon": "🤲", "name": "Gyan Mudra",     "dosha": "Vata/Pitta", "body": "Index fingertip to thumb; relax. Enhances focus; reduces stress; balances memory circuits."},
    {"icon": "🙏", "name": "Vayu Mudra",     "dosha": "Vata",       "body": "Fold index; press with thumb base. Classical prescription for anxiety and nervous tremors."},
    {"icon": "☯",  "name": "Prana Mudra",    "dosha": "Kapha",      "body": "Ring & little fingertips to thumb. Uplifts depleted energy; revitalises vital force; boosts immunity."},
]

LEELA_SQUARES = {
    1: {"type": "special", "name": "Birth (Janma)",             "desc": "The jiva enters the physical plane, bound by the elements to begin its journey."},
    6: {"type": "ladder",  "name": "Compassion (Karuna)",       "dest": 25, "desc": "Recognizing the suffering of others elevates the soul towards universal kinship."},
    15:{"type": "ladder",  "name": "Faith (Shraddha)",          "dest": 36, "desc": "Unwavering trust in dharma carries the soul swiftly forward."},
    17:{"type": "snake",   "name": "Anger (Krodha)",            "dest": 4,  "desc": "A destructive fire of the mind causes the atman to fall back into harmful states."},
    22:{"type": "ladder",  "name": "Knowledge (Jnana)",         "dest": 55, "desc": "Piercing the veil of ignorance with viveka brings vast clarity."},
    29:{"type": "snake",   "name": "Greed (Lobha)",             "dest": 8,  "desc": "Insatiable desire drags expanding consciousness back into a tamas mindset."},
    30:{"type": "ladder",  "name": "Generosity (Dana)",         "dest": 52, "desc": "Selfless giving frees the mind from possessiveness."},
    36:{"type": "special", "name": "Karma",                     "desc": "The universal principle of karma — every action bears a consequence."},
    38:{"type": "snake",   "name": "Pride (Mada)",              "dest": 12, "desc": "Ignorant arrogance blinds the buddhi, leading to an inevitable fall."},
    40:{"type": "ladder",  "name": "Gratitude (Kritajnata)",    "dest": 62, "desc": "Heartfelt thankfulness expands the soul, elevating it to true sattva."},
    44:{"type": "snake",   "name": "Jealousy (Matsarya)",       "dest": 21, "desc": "Toxic jealousy breeds bitterness, lowering the soul into dark dosha."},
    46:{"type": "ladder",  "name": "Devotion (Bhakti)",         "dest": 68, "desc": "Pure love and surrender to the divine propels the seeker to the gateway of moksha."},
    51:{"type": "ladder",  "name": "Truth (Satya)",             "dest": 67, "desc": "Unshakable adherence to reality burns away all falsehoods."},
    53:{"type": "snake",   "name": "Attachment (Moha)",         "dest": 31, "desc": "Destructive attachment to transient objects traps the chitta in bondage."},
    54:{"type": "special", "name": "Illusion (Maya)",           "desc": "The grand cosmic maya makes the transient world appear as ultimate reality."},
    57:{"type": "ladder",  "name": "Wisdom (Prajna)",           "dest": 71, "desc": "Deep intuitive insight into the nature of prakriti uplifts consciousness."},
    60:{"type": "snake",   "name": "Lust (Kama)",               "dest": 35, "desc": "Sensual desire overrides viveka, throwing the seeker back down."},
    65:{"type": "snake",   "name": "Deceit (Dambha)",           "dest": 27, "desc": "Hypocrisy builds a fragile reality that shatters, plunging manas into darkness."},
    68:{"type": "special", "name": "Gateway of Enlightenment",  "desc": "The threshold where the jiva gently dissolves into a glimpse of divine truth."},
    70:{"type": "snake",   "name": "Ego (Ahamkara)",            "dest": 42, "desc": "The stubborn ahamkara causes a steep descent from near-liberation."},
    72:{"type": "special", "name": "Moksha 🕉",                  "desc": "Liberation — freedom from the cycle of birth and death. OM."},
}

SQUARE_NAMES = {
    1:"Birth", 2:"Senses", 3:"Form", 4:"Himsa", 5:"Delusion", 6:"Compassion", 7:"Desire",
    8:"Scarcity", 9:"Manas", 10:"Purity", 11:"Rajas", 12:"Abhimana", 13:"Tamas", 14:"Buddhi",
    15:"Faith", 16:"Tapas", 17:"Anger", 18:"Joy", 19:"Equanimity", 20:"Seva", 21:"Bitterness",
    22:"Knowledge", 23:"Vairagya", 24:"Kusanga", 25:"Maitri", 26:"Sorrow", 27:"Falsehood",
    28:"Dharma", 29:"Greed", 30:"Generosity", 31:"Bondage", 32:"Niyama", 33:"Asmita",
    34:"Yama", 35:"Bhoga", 36:"Karma", 37:"Intuition", 38:"Pride", 39:"Prana", 40:"Gratitude",
    41:"Surrender", 42:"Separation", 43:"Dharana", 44:"Jealousy", 45:"Laya", 46:"Devotion",
    47:"Svadhyaya", 48:"Ananda", 49:"Meditation", 50:"Nada", 51:"Truth", 52:"Abundance",
    53:"Attachment", 54:"Maya", 55:"Clarity", 56:"Sadhana", 57:"Wisdom", 58:"Tejas",
    59:"Peace", 60:"Lust", 61:"Divine Love", 62:"Contentment", 63:"Transcendence",
    64:"Omnipresence", 65:"Deceit", 66:"Grace", 67:"Cosmic Order", 68:"Enlightenment",
    69:"Brahman", 70:"Ego", 71:"Self-Realization", 72:"Moksha 🕉"
}

# ─────────────────────────────────────────────
# FALLBACK DOSHA CLASSIFIER
# ─────────────────────────────────────────────

KEYWORDS = {
    "Vata":  ["anxious","anxiety","restless","fear","insomnia","worry","scattered","nervous",
              "cold","overthinking","forgetful","fatigue","panic","racing","overwhelmed",
              "dry","constipation","irregular","dizzy","trembling","spacey"],
    "Pitta": ["angry","anger","irritable","hot","burnout","frustrated","acid","rash","intense",
              "sweating","inflamed","heated","agitated","temper","burning","bitter","jealous",
              "competitive","sharp","inflammation","perfectionistic"],
    "Kapha": ["lethargic","lethargy","heavy","foggy","depressed","slow","dull","unmotivated",
              "congested","sad","sluggish","stuck","withdrawn","numb","weight","sleepy",
              "attachment","cold","excessive","overweight"]
}

FALLBACK_DATA = {
    "Vata": {
        "color": "#B39DDB",
        "rasa": "Anxiety & nervous restlessness",
        "herb": "Ashwagandha (Withania somnifera) — 1 tsp in warm milk before bed",
        "mudra": "Vayu Mudra — fold index finger, press with thumb base",
        "prana": "Nadi-Shodhana: 10 min alternate nostril breathing",
        "raga": "Hamsadhwani",
        "sadhana": "5 min sunrise stillness, chant 'So-Hum' with each breath. Avoid cold foods and excessive stimulation."
    },
    "Pitta": {
        "color": "#FF8A50",
        "rasa": "Irritability & overheating",
        "herb": "Brahmi (Bacopa monnieri) — 1 tsp powder as morning tea with honey",
        "mudra": "Shuni Mudra — middle fingertip to thumb",
        "prana": "Bhramari: 5 min humming bee breath, 10–15 rounds",
        "raga": "Puriya",
        "sadhana": "Evening moon-gazing, 10 min cooling pranayama, reduce spicy food and competitive environments."
    },
    "Kapha": {
        "color": "#81C784",
        "rasa": "Lethargy & heaviness",
        "herb": "Trikatu (Ginger+Pepper+Pippali) — pinch with honey before meals",
        "mudra": "Prana Mudra — ring & little fingertips to thumb",
        "prana": "Bhastrika: 3–5 min vigorous bellows breath each morning",
        "raga": "Malkauns",
        "sadhana": "Vigorous sunrise movement, dry brushing, Bhastrika on waking. Break one comfort habit each week."
    }
}

def classify_dosha(text):
    scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
    matched = {"Vata": [], "Pitta": [], "Kapha": []}
    lower = text.lower()
    for dosha, words in KEYWORDS.items():
        for w in words:
            if re.search(r'\b' + re.escape(w) + r'\b', lower) and w not in matched[dosha]:
                scores[dosha] += 2
                matched[dosha].append(w)
    winner = max(scores, key=scores.get)
    conf = min(50 + scores[winner] * 5, 97)
    fb = FALLBACK_DATA[winner]
    return {
        "dosha": winner,
        "confidence": conf,
        "symptoms": matched[winner][:4] or ["general imbalance"],
        "data": fb,
        "response": (
            f"🔮 PILLAR I — VIKALPA\n"
            f"Dominant dosha: **{winner}** ({conf}% confidence). Rasa: {fb['rasa']}. "
            f"Your {winner} vayu is aggravated.\n\n"
            f"🎵 PILLAR II — RAGA\n"
            f"Prescribed: **{fb['raga']}** — search \"{fb['raga']} classical instrumental\" on YouTube. "
            f"Sit in stillness for 20–30 minutes.\n\n"
            f"🌿 PILLAR III — DHARANA\n"
            f"• **Herb:** {fb['herb']}\n"
            f"• **Mudra:** {fb['mudra']}\n"
            f"• **Pranayama:** {fb['prana']}\n"
            f"• **Diet:** Favour warm, grounding, seasonal foods.\n\n"
            f"📿 PILLAR IV — SADHANA\n"
            f"{fb['sadhana']}\n\n"
            f"*Educational purposes only. Consult a qualified Vaidya for clinical care.*"
        )
    }


# ─────────────────────────────────────────────
# CLAUDE API CALLER
# ─────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "vaidya": """You are the Digital Vaidya — an expert Ayurvedic AI powered by 5,000 years of classical Indian medicine (Charaka Samhita, Ashtanga Hridayam, Sushruta Samhita) combined with modern peer-reviewed clinical research on herbs, pranayama, and raga chikitsa (music therapy).

Analyze the user's described symptoms and emotional state, then provide a comprehensive FOUR-PILLAR Ayurvedic prescription. Format EXACTLY as:

🔮 PILLAR I — VIKALPA
Identify the dominant dosha imbalance (Vata/Pitta/Kapha). Explain WHY from their symptoms. State confidence %. Note the rasa (emotional flavour).

🎵 PILLAR II — RAGA
Prescribe one specific raga from: Ahir Bhairav, Hamsadhwani, Bilahari, Sama, Mohanam, Bhimpalas, Yaman, Kalyani, Puriya, Darbari Kanada, Malkauns, Bageshri, Nilambari. Explain why it suits their dosha & current time. Listening instruction.

🌿 PILLAR III — DHARANA
• Herb: Name (Sanskrit name) — preparation, dose, timing, one clinical reference
• Mudra: Name — exact instruction
• Pranayama: Name — step-by-step method, duration
• Diet: One specific adjustment for their dosha

📿 PILLAR IV — SADHANA
A 21-day personalised daily practice: morning ritual, evening wind-down, classical text reference, one mindset shift.

End with: *Educational purposes only. Consult a qualified Vaidya for clinical care.*

Tone: warm, knowledgeable, like a wise ancient physician who also understands neuroscience. Use Sanskrit terms with English translation. Be specific and clinically grounded.""",

    "raga": """You are the Digital Vaidya, expert in Raga Chikitsa (classical Indian sound therapy). When asked about a specific raga provide:

1. **Raga & Its Nature** — scale (arohana/avarohana), rasa (emotional quality), time prescription
2. **Dosha Connection** — which dosha(s) it pacifies and why (acoustic neuroscience)
3. **Clinical Evidence** — RCT studies, research, or traditional therapeutic claims
4. **How to Listen** — exact instructions, duration, posture, breathing
5. **YouTube Search** — exact query: "[Raga Name] classical instrumental"
6. **Contraindications** — when NOT to listen

Keep it practical, scientifically grounded and warm. 2-3 focused paragraphs.""",

    "herb": """You are the Digital Vaidya, expert in Ayurvedic Dravyaguna (herbal pharmacology). Provide:

1. **Identity** — Sanskrit name, botanical name, rasa (taste), virya (potency), vipaka (post-digestive effect)
2. **Dosha Action** — which doshas it pacifies/aggravates and the mechanism
3. **Preparation & Dosage** — traditional preparation, modern form, exact dosage, timing
4. **Clinical Evidence** — specific studies, PubMed references where available
5. **Contraindications & Interactions** — who should NOT take it
6. **Daily Practice** — how to incorporate into daily dinacharya (routine)

Be specific, clinically referenced, and practically useful."""
}

def call_claude(user_message, prompt_type="vaidya"):
    if not ANTHROPIC_API_KEY:
        return None, "No API key configured"

    system = SYSTEM_PROMPTS.get(prompt_type, SYSTEM_PROMPTS["vaidya"])
    payload = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 1200,
        "system": system,
        "messages": [{"role": "user", "content": user_message}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data.get("content", [{}])[0].get("text", "")
            return text, None
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode("utf-8"))
        return None, err.get("error", {}).get("message", str(e))
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = (data.get("message") or "").strip()
    prompt_type = data.get("type", "vaidya")

    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Try Claude AI first
    ai_text, err = call_claude(message, prompt_type)

    if ai_text:
        return jsonify({
            "response": ai_text,
            "source": "claude",
            "sattva": 10
        })
    else:
        # Fallback to local engine
        result = classify_dosha(message)
        return jsonify({
            "response": result["response"],
            "source": "fallback",
            "dosha": result["dosha"],
            "confidence": result["confidence"],
            "sattva": 8,
            "fallback_reason": err
        })

@app.route("/api/data/ragas")
def get_ragas():
    return jsonify(RAGAS)

@app.route("/api/data/herbs")
def get_herbs():
    return jsonify(HERBS)

@app.route("/api/data/pranayamas")
def get_pranayamas():
    return jsonify(PRANAYAMAS)

@app.route("/api/data/leela")
def get_leela():
    return jsonify({
        "squares": LEELA_SQUARES,
        "names": SQUARE_NAMES
    })

@app.route("/api/classify", methods=["POST"])
def classify():
    data = request.get_json()
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400
    result = classify_dosha(text)
    return jsonify(result)

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "claude_configured": bool(ANTHROPIC_API_KEY),
        "model": CLAUDE_MODEL
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
