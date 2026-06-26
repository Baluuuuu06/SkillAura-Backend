from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from utils.db import db

def get_quiz(skill_name):
    quiz = db.quizzes.find_one({"skill": skill_name}, {"_id": 0})
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404
    return jsonify(quiz), 200

@jwt_required()
def submit_quiz():
    user_id = get_jwt_identity()
    data = request.get_json()
    score = data.get('score', 0)
    skill = data.get('skill', '')
    
    db.progress.insert_one({
        "user_id": ObjectId(user_id),
        "skill": skill,
        "score": score,
        "type": "quiz"
    })
    
    xp_earned = int((score / 100) * 50)
    badge_earned = 1 if score >= 80 else 0
    
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$inc": {"xp": xp_earned, "badges_earned": badge_earned},
            "$addToSet": {"skills": skill}
        }
    )
    
    from datetime import datetime
    db.activity.insert_one({
        "user_id": ObjectId(user_id),
        "skill": skill,
        "hours": 2, # Assuming 2 hours learning credit for a quiz
        "date": datetime.now()
    })
    
    return jsonify({"message": "Quiz submitted successfully", "score": score, "xp_earned": xp_earned}), 200
