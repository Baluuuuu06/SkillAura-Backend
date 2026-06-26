from flask import Blueprint
from controllers.auth_controller import register, login, update_profile, send_otp, verify_otp

auth_bp = Blueprint('auth_bp', __name__)

auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/profile', methods=['PUT'])(update_profile)
auth_bp.route('/send-otp', methods=['POST'])(send_otp)
auth_bp.route('/verify-otp', methods=['POST'])(verify_otp)
