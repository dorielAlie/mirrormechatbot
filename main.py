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

        return jsonify({"reply": response_text})

    except Exception as e:
        print(f"🔥 ERROR in /chat: {str(e)}")  # ✅ Log the error clearly
        return jsonify({"error": "Internal Server Error"}), 500

def get_openai_response(user_input):
    """ Fetch a response from OpenAI ChatGPT """
    client = openai.OpenAI()  # ✅ Updated for OpenAI v1.0+
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Use dynamic port for Render
    app.run(host="0.0.0.0", port=port)
