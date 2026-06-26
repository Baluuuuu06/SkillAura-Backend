from flask import request, jsonify
from flask_jwt_extended import jwt_required
import g4f

@jwt_required()
def ask_chatbot():
    data = request.get_json()
    user_message = data.get('message', '')
    
    try:
        # Advanced Prompt engineering to make it act like a top-tier mentor
        system_prompt = (
            "You are the official AI Mentor for 'SkillAura', a premium learning platform dedicated to making users '1% better than yesterday'. "
            "Your personality is incredibly friendly, encouraging, empathetic, and highly expert in all things programming and tech. "
            "Guidelines for your responses:\n"
            "1. Format answers beautifully using Markdown. Use bolding for emphasis, bullet points for lists, and fenced code blocks for any code.\n"
            "2. Keep your explanations crystal clear, accurate, and easy to understand for beginners, but deep enough for advanced users.\n"
            "3. If providing code, always include a brief explanation of how it works.\n"
            "4. End your responses with an encouraging remark to keep the user motivated on their learning journey."
        )
        
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response
    except Exception as e:
        reply = f"Sorry, I encountered an error fetching your answer: {str(e)}"
    
    return jsonify({"reply": reply}), 200
