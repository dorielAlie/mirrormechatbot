from flask import Flask, request, jsonify
import json
import openai
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}})  # ✅ Allow all external requests

# Load predefined chatbot responses from JSON file
try:
    with open("responses.json", "r") as file:
        chatbot_responses = json.load(file)
except FileNotFoundError:
    chatbot_responses = {}

# Read API keys from environment variables
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
    client = openai.OpenAI()  # ✅ Correct OpenAI v1.0 format

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content

@app.route("/chat", methods=["POST"])
def chat():
    """ Handle chatbot messages from Wix """
    try:
        # Ensure JSON request format
        if request.content_type != "application/json":
            return jsonify({"error": "Unsupported Media Type. Use 'application/json'."}), 415

        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. Missing 'message' key."}), 400

        user_input = data.get("message", "")

        # Step 1: Check predefined responses
        response_text = get_trained_response(user_input)

        # Step 2: If no match, use OpenAI
        if response_text is None:
            response_text = "Checking outside... " + get_openai_response(user_input)

        return jsonify({"reply": response_text})

    except Exception as e:
        print(f"Error in /chat: {str(e)}")  # ✅ Log the error
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Use dynamic port for Render
    app.run(host="0.0.0.0", port=port)
