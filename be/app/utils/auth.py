from functools import wraps
from flask import request, jsonify, current_app
from app.utils.auth import decode_jwt_token  

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "로그인 필요"}), 401
        
        try:
            user_data = decode_jwt_token(token)  
            current_app.config["USER"] = user_data  
        except Exception as e:
            return jsonify({"error": "잘못된 토큰"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
