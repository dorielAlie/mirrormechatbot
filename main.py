from flask import Flask, request, jsonify
import json
import openai
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)  # ✅ Allow all external requests

# Load predefined chatbot responses from JSON file
try:
    with open("responses.json", "r") as file:
        chatbot_responses = json.load(file)
except FileNotFoundError:
    chatbot_responses = {}

# Read API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """ Handle chatbot messages from Wix and manual tests """
    try:
        if request.method == "GET":
            return jsonify({"message": "Chatbot API is running. Use POST to send messages."}), 200

        if request.content_type != "application/json":
            return jsonify({"error": "Unsupported Media Type. Use 'application/json'."}), 415

        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. Missing 'message' key."}), 400

        user_input = data.get("message", "")

        # Step 1: Check predefined responses
        response_text = chatbot_responses.get(user_input, None)

        # Step 2: If no match, use OpenAI
        if response_text is None:
            response_text = "Checking outside... " + get_openai_response(user_input)

    # Step 3: Generate AI voice for the response
    voice_file = generate_voice(response_text)

    return jsonify({
        "reply": response_text,
        "voice": voice_file if voice_file else None  # ✅ Returns audio file if successful
    })
    
    except Exception as e:
        print(f"🔥 ERROR in /chat: {str(e)}")  # ✅ Log the error clearly
        return jsonify({"error": "Internal Server Error"}), 500

def get_openai_response(user_input):
    """Test function to check if OpenAI API works"""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",  # ✅ Ensure you're using a valid model
            messages=[{"role": "user", "content": user_input}]
        )
        print(f"✅ OpenAI Response: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"🔥 ERROR: OpenAI API failed - {str(e)}")
        return "Error: OpenAI request failed"

def generate_voice(text):
    """ Convert chatbot response to AI voice using ElevenLabs """
    try:
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        voice_url = "https://api.elevenlabs.io/v1/text-to-speech/tx"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2",  # ✅ Fastest model
            "voice_id": "Rachel"  # ✅ You can change this to another ElevenLabs voice
        }

        response = requests.post(voice_url, headers=headers, json=data)

        if response.status_code == 200:
            audio_filename = "response.mp3"
            with open(audio_filename, "wb") as f:
                f.write(response.content)
            return audio_filename
        else:
            print(f"🔥 ERROR: ElevenLabs API failed - {response.text}")
            return None
    except Exception as e:
        print(f"🔥 ERROR: ElevenLabs request failed - {str(e)}")
        return None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Use dynamic port for Render
    app.run(host="0.0.0.0", port=port)
