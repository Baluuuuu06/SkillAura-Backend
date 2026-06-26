import datetime
import random
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from utils.db import db
from utils.extensions import bcrypt

otp_store = {}

def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"message": "Email is required"}), 400
        
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    }
    
    print(f"\n{'='*40}")
    print(f"🔒 MOCK EMAIL SENT TO: {email}")
    print(f"🔑 OTP CODE: {otp}")
    print(f"{'='*40}\n")
    
    return jsonify({"message": f"OTP sent to {email}"}), 200

def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"message": "Email and OTP are required"}), 400
        
    stored_data = otp_store.get(email)
    
    if not stored_data:
        return jsonify({"message": "No OTP found for this email"}), 400
        
    if datetime.datetime.utcnow() > stored_data["expires_at"]:
        del otp_store[email]
        return jsonify({"message": "OTP has expired"}), 400
        
    if stored_data["otp"] != otp:
        return jsonify({"message": "Invalid OTP"}), 400
        
    del otp_store[email]
    return jsonify({"message": "OTP verified successfully"}), 200

def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not name or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    if db.users.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "role": role,
        "skills": [],
        "completed_modules": [],
        "xp": 0,
        "bio": "",
        "location": "",
        "occupation": "",
        "github": "",
        "portfolio": "",
        "created_at": datetime.datetime.utcnow()
    }

    result = db.users.insert_one(new_user)
    return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)}), 201

def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = db.users.find_one({"email": email})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user['_id']), 
        additional_claims={"role": user['role']}
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": str(user['_id']),
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "bio": user.get('bio', ''),
            "location": user.get('location', ''),
            "occupation": user.get('occupation', ''),
            "github": user.get('github', ''),
            "portfolio": user.get('portfolio', ''),
            "profile_picture": user.get('profile_picture', '')
        }
    }), 200

from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    update_fields = {}
    if data.get('name'):
        update_fields['name'] = data.get('name')
    if data.get('email'):
        update_fields['email'] = data.get('email')
    if data.get('profile_picture'):
        update_fields['profile_picture'] = data.get('profile_picture')
        
    for field in ['bio', 'location', 'occupation', 'github', 'portfolio']:
        if field in data:
            update_fields[field] = data[field]
        
    if data.get('newPassword'):
        if not data.get('currentPassword'):
            return jsonify({"message": "Current password is required to set a new password."}), 400
        
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not bcrypt.check_password_hash(user['password'], data.get('currentPassword')):
            return jsonify({"message": "Incorrect current password."}), 401
            
        hashed_pw = bcrypt.generate_password_hash(data.get('newPassword')).decode('utf-8')
        update_fields['password'] = hashed_pw
        
    if update_fields:
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
        
    return jsonify({"message": "Profile updated successfully!"}), 200
