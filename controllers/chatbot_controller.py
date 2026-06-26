from flask import request, jsonify
from flask_jwt_extended import jwt_required
from google import genai
from config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)

@jwt_required()
def ask_chatbot():
    data = request.get_json()
    user_message = data.get("message", "")

    system_prompt = """
You are the official AI Mentor for SkillAura.

Rules:
- Friendly and motivating.
- Explain concepts clearly.
- Format using Markdown.
- Use bullet points where needed.
- Put code inside code blocks.
- Encourage users at the end.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nUser: {user_message}"
        )

        return jsonify({
            "reply": response.text
        }), 200

    except Exception as e:
        return jsonify({
            "reply": f"Error: {str(e)}"
        }), 500