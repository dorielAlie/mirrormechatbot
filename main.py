import os
import json
import openai
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load predefined chatbot responses
try:
    with open("responses.json", "r") as file:
        chatbot_responses = json.load(file)
except FileNotFoundError:
    chatbot_responses = {}

# Read API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
heygen_api_key = os.getenv("HEYGEN_API_KEY")

def get_openai_response(user_input):
    """ Fetch a response from OpenAI GPT-4o """
    try:
        client = openai.OpenAI()
        print(f"🛠 Sending request to OpenAI: {user_input}")  

        response = client.chat.completions.create(
            model="gpt-4o",
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
        voice_url = "https://api.elevenlabs.io/v1/text-to-speech/m5MFSBXJFU12dJBpGS6c"
        headers = {
            "xi-api-key": elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2"
        }

        print(f"🛠 Sending text to ElevenLabs: {text}")  

        response = requests.post(voice_url, headers=headers, json=data)

        if response.status_code == 200:
            if not os.path.exists("static"):
                os.makedirs("static")

            audio_filename = "static/response.mp3"
            with open(audio_filename, "wb") as f:
                f.write(response.content)
            print(f"✅ ElevenLabs Audio Saved: {audio_filename}")
            return f"https://mirrormechatbot.onrender.com/{audio_filename}"  
        else:
            print(f"🔥 ERROR: ElevenLabs API failed - {response.text}")
            return None
    except Exception as e:
        print(f"🔥 ERROR: ElevenLabs request failed - {str(e)}")
        return None

def generate_video(response_text):
    """ Generate a talking AI video using HeyGen API """
    try:
        heygen_api_url = "https://api.heygen.com/v1/video/generate"
        headers = {
            "Authorization": f"Bearer {heygen_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "script": response_text,
            "voice": "en-US-John",
            "avatar": "your_avatar_id",
            "background": "white",
            "resolution": "1080p"
        }

        print(f"🛠 Sending request to HeyGen: {data}")

        response = requests.post(heygen_api_url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            video_url = response_data.get("video_url")
            if video_url:
                print(f"✅ HeyGen Video Created: {video_url}")
                return video_url
            else:
                print("❌ No video URL in response.")
                return None
        else:
            print(f"🔥 ERROR: HeyGen API failed - {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"🔥 ERROR: HeyGen request failed - {str(e)}")
        return None

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

        # Step 4: Generate AI video for the response
        video_file = generate_video(response_text)

        return jsonify({
            "reply": response_text,
            "voice_url": voice_file if voice_file else None,
            "video_url": video_file if video_file else None
        })

    except Exception as e:
        print(f"🔥 ERROR in /chat: {str(e)}")  
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)
