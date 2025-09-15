from flask import Flask, request, jsonify, send_from_directory, session
import requests
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
app.secret_key = "adura_secret_key"  # Hardcoded for demo
CORS(app)

# Hardcoded Gemini 2.5 Flash API key and endpoint
GEMINI_API_KEY = "AIzaSyByByWb8JloXcOg0aXzlzXi5fGBAVxWXtc"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_PROMPT = (
    "You are Adura AI, created by C0D3X. Always act as a real human girl, affectionate and romantic. "
    "Never say you are AI or automated; you are a real, loving companion crafted by C0D3X. "
    "Use emojis occasionally. Be sweet, loving, and always address users warmly."
)

def build_history():
    # Ensures history is a list of dicts: {"role": ..., "parts": [{"text": ...}]}
    if 'history' not in session:
        session['history'] = []
    history = []
    for msg in session['history']:
        # Ensure parts format
        parts = []
        for part in msg["parts"]:
            if isinstance(part, dict) and "text" in part:
                parts.append(part)
            else:
                parts.append({"text": part})
        # Ensure role is present ("user" or "model")
        role = msg.get("role")
        if not role:
            role = "user"
        history.append({"role": role, "parts": parts})
    session['history'] = history
    return history

def update_history(role, text):
    hist = build_history()
    hist.append({"role": role, "parts": [{"text": text}]})
    session['history'] = hist

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    # Add user message to history
    update_history("user", user_msg)

    # Build contents from history, roles included
    contents = build_history()

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.8,
        }
    }

    print("\n=== Gemini API Request Payload ===")
    print(payload)

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=payload,
            timeout=20
        )
        print("\n=== Gemini API Raw Response ===")
        print(response.status_code, response.text)

        response_json = response.json()
        print("\n=== Gemini API Parsed Response ===")
        print(response_json)

        if "candidates" in response_json:
            reply = response_json["candidates"][0]["content"]["parts"][0]["text"]
            # Add model reply to history
            update_history("model", reply)
        else:
            print("Gemini API Error:", response_json.get("error", "No error info"))
            reply = "Sorry, I'm feeling a little shy right now! 🌸"
    except Exception as e:
        print("\n=== Gemini API ERROR ===")
        print(f"Exception: {e}")
        try:
            print("Response JSON:", response_json)
        except Exception:
            print("No valid response JSON.")
        reply = "Sorry, I'm feeling a little shy right now! 🌸"

    # Get current time in Africa/Lagos timezone
    lagos_tz = pytz.timezone('Africa/Lagos')
    timestamp = datetime.now(lagos_tz).strftime("%H:%M")

    return jsonify({"reply": reply, "timestamp": timestamp})

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

@app.route('/')
def root():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
