from flask import Flask, request, jsonify
import json
import openai
import requests
import os

app = Flask(__name__)

# Load predefined chatbot responses from JSON file
with open("responses.json", "r") as file:
    chatbot_responses = json.load(file)

# Read API keys from Replit's environment variables (DO NOT HARD-CODE!)
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Chatbot is running! Use /chat to talk to it."

def get_trained_response(user_input):
    """ Check if the user question exists in the chatbot database """
    return chatbot_responses.get(user_input, None)

def get_openai_response(user_input):
    """ Fetch a response from OpenAI ChatGPT """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
    )
    return response["choices"][0]["message"]["content"]

def generate_voice(text):
    """ Generate an AI voice response using ElevenLabs """
    voice_url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice": "Rachel"  # You can change this to a different voice name
    }

    response = requests.post(voice_url, headers=headers, json=data)

    if response.status_code == 200:
        with open("response.mp3", "wb") as f:
            f.write(response.content)
        return "response.mp3"
    else:
        return None  # If voice generation fails

@app.route("/chat", methods=["POST"])
def chat():
    """ Handle chatbot messages from Wix """
    user_input = request.json.get("message", "")

    # Step 1: Check predefined responses
    response_text = get_trained_response(user_input)

    # Step 2: If no match, use OpenAI and say "Checking outside..."
    if response_text is None:
        response_text = "Checking outside... " + get_openai_response(user_input)

    # Step 3: Generate AI voice for the response
    voice_file = generate_voice(response_text)

    return jsonify({"reply": response_text, "voice": voice_file})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Replit’s assigned port
    app.run(host="0.0.0.0", port=port)