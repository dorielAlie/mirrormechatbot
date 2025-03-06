from flask_cors import CORS
from flask import Flask, request, jsonify
import json
import openai
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Load predefined chatbot responses from JSON file
with open("responses.json", "r") as file:
    chatbot_responses = json.load(file)

# Read API keys from Replit's environment variables (DO NOT HARD-CODE!)
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """ Handle chatbot messages from Wix """
    try:
        if request.method == "GET":
            return jsonify({"error": "Use POST instead."}), 405

        if request.content_type != "application/json":
            return jsonify({"error": "Unsupported Media Type. Use 'application/json'."}), 415

        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. Missing 'message' key."}), 400

        user_input = data.get("message", "")

        # Step 1: Check predefined responses
        response_text = get_trained_response(user_input)

        # Step 2: If no match, use OpenAI and say "Checking outside..."
        if response_text is None:
            response_text = "Checking outside... " + get_openai_response(user_input)

        return jsonify({"reply": response_text})

    except Exception as e:
        print(f"Error in /chat: {str(e)}")  # Log the error
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """ Handle chatbot messages from Wix """
    if request.content_type != "application/json":
        return jsonify({"error": "Unsupported Media Type. Use 'application/json'."}), 415

    data = request.get_json()
    user_input = data.get("message", "")

    # Step 1: Check predefined responses
    response_text = get_trained_response(user_input)

    # Step 2: If no match, use OpenAI and say "Checking outside..."
    if response_text is None:
        response_text = "Checking outside... " + get_openai_response(user_input)

    return jsonify({"reply": response_text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Replit’s assigned port
    app.run(host="0.0.0.0", port=port)