from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

def token_required(f):
    """Decorator để verify JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid token"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get('sub')
            
            if not username:
                return jsonify({"error": "Invalid token payload"}), 401
            
            current_user = {"username": username}
            return f(*args, current_user=current_user, **kwargs)
            
        except JWTError as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
    
    return decorated