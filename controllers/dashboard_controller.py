from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from utils.db import db
from datetime import datetime, timedelta

@jwt_required()
def get_dashboard_stats():
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    skills_started = len(user.get('skills', []))
    xp = user.get('xp', 0)
    badges = user.get('badges_earned', 0)
    
    all_progress = list(db.progress.find({"user_id": ObjectId(user_id), "type": "roadmap"}))
    skills_completed = 0
    learning_hours = 0
    
    skill_labels = []
    skill_data = []
    
    for prog in all_progress:
        skill_name = prog.get("skill")
        completed_indices = prog.get("completed_modules", [])
        
        if len(completed_indices) > 0:
            skill_labels.append(skill_name)
            skill_data.append(len(completed_indices))
            
        roadmap = db.roadmaps.find_one({"skill": skill_name})
        if roadmap:
            total_modules = len(roadmap.get("modules", []))
            if len(completed_indices) >= total_modules and total_modules > 0:
                skills_completed += 1
                
            for idx in completed_indices:
                if idx < total_modules:
                    time_str = roadmap["modules"][idx].get("estimated_time", "1 Week")
                    try:
                        weeks = int(time_str.split()[0])
                        learning_hours += weeks * 10 # 10 hours per week
                    except:
                        learning_hours += 10
    
    quizzes_taken = db.progress.count_documents({"user_id": ObjectId(user_id), "type": "quiz"})
    learning_hours += quizzes_taken
    
    if not skill_labels:
        skill_labels = ["Get Started!"]
        skill_data = [100]
    
    stats = {
        "skills_started": skills_started,
        "skills_completed": skills_completed,
        "current_streak": 1 if xp > 0 else 0,
        "learning_hours": learning_hours,
        "xp_points": xp,
        "badges_earned": badges
    }
    
    # Calculate Weekly Progress from db.activity
    today = datetime.now()
    weekly_labels = []
    weekly_data = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        weekly_labels.append(day.strftime("%a"))
        
        start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        activities = db.activity.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": start_of_day, "$lt": end_of_day}
        })
        
        hours_today = sum(act.get("hours", 0) for act in activities)
        weekly_data.append(hours_today)
        
    charts = {
        "weekly_progress": {
            "labels": weekly_labels,
            "data": weekly_data
        },
        "skill_completion": {
            "labels": skill_labels,
            "data": skill_data
        }
    }
    
    return jsonify({"stats": stats, "charts": charts}), 200
