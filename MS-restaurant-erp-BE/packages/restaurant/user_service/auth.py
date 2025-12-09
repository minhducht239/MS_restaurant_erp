import os
from jose import jwt, JWTError

SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

def decode_token(token):
    """Giải mã JWT token và trả về user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        return {"username": username}
    except JWTError:
        return None

def get_user_from_request(args):
    """Lấy user từ Authorization header trong serverless args"""
    auth_header = args.get("__ow_headers", {}).get("authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return decode_token(token)