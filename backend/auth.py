import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from database import get_user_by_id

SECRET_KEY = os.environ.get('SECRET_KEY', 'student_planner_secret_key_2026_shubham_singh_secure_min_32_bytes_length')

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id: int) -> str:
    payload = {
        'sub': str(user_id),
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return int(payload['sub'])
    except Exception as e:
        print(f"[AUTH ERROR] Token decoding failed: {e}")
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        parts = auth_header.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid Authorization header format'}), 401
        
        token = parts[1]
        user_id = decode_token(token)
        if not user_id:
            return jsonify({'error': 'Token is invalid or has expired'}), 401
        
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User associated with token not found'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return decorated
