import requests
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

# Your HeyGen Avatar & Voice IDs
HEYGEN_AVATAR_ID = "dfb8a1be09ac451d8634229589328ffb"  # Replace with your HeyGen Avatar ID
HEYGEN_VOICE_ID = "639d0dc76eff4b4f8d237249c0e00fe9"  # Replace with your HeyGen Voice ID

def generate_heygen_video(text):
    """ Generate a talking avatar video using HeyGen API """
    try:
        url = "https://api.heygen.com/v1/videos"
        headers = {
            "Authorization": f"Bearer {HEYGEN_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "avatar_id": HEYGEN_AVATAR_ID,
            "voice_id": HEYGEN_VOICE_ID,
            "language": "en",
            "speed": 1.0
        }

        print(f"🛠 Sending request to HeyGen: {text}")
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            video_url = response_json.get("video_url")
            print(f"✅ HeyGen Video Generated: {video_url}")
            return video_url
        else:
            print(f"🔥 ERROR: HeyGen API failed - {response.text}")
            return None
    except Exception as e:
        print(f"🔥 ERROR: HeyGen request failed - {str(e)}")
        return None

@app.route("/chat", methods=["POST"])
def chat():
    """ Handle chatbot messages and generate video responses """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. Missing 'message' key."}), 400

        user_input = data.get("message", "")
        chatbot_response = f"Here's my response to: {user_input}"

        # Generate Video using HeyGen
        video_url = generate_heygen_video(chatbot_response)

        return jsonify({
            "reply": chatbot_response,
            "video_url": video_url if video_url else None
        })
    except Exception as e:
        print(f"🔥 ERROR in /chat: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
