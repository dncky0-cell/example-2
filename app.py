# this was made by smartiefellow (on discord and roblox)
# this is an ai integration script, used for websites, jsuk, i didnt mention website code as that isnt related with python
# the ai bot should be a minecraft bot that should help you on your minecraft journey!

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

BOT_NAME  = "Minecraft Master"
MODEL     = "gemini-2.5-flash" 

PORT      = 8080
MAX_MSGS  = 24

app = Flask(__name__)
CORS(app)   

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = f"""You are {BOT_NAME}, an master in minecraft Java, bedrock, and education Edition. help players with building, redstone, farms, enchanting, survival, and issues they occur. explain everything step by step in simple language. Always list materials before giving building instructions.

always structure your responses using these headings:

materials Needed

steps

tips

use numbered lists for instructions and bullet points for materials."""


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        model_name = data.get("model", MODEL)

        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        trimmed = messages[-MAX_MSGS:]

        formatted_contents = []
        for msg in trimmed:
            role = msg.get("role")
            
            if role == "system":
                continue
                
            if role == "assistant":
                role = "model"
    
            content_text = msg.get("content") or msg.get("text") or ""
            
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=content_text)]
                )
            )

        tools = [
            types.Tool(googleSearch=types.GoogleSearch()),
        ]

        generate_content_config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=[
                types.Part.from_text(text=SYSTEM_PROMPT),
            ],
        )

        response = client.models.generate_content(
            model=model_name,
            contents=formatted_contents,
            config=generate_content_config,
        )
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        
        if response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            total_tokens = getattr(response.usage_metadata, "total_token_count", 0)

        return jsonify({
            "response": response.text,
            "model": model_name,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME, "model": MODEL})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)
