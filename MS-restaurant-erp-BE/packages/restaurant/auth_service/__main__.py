import json
from schemas import UserCreate, UserLogin
from auth_utils import hash_password, verify_password, create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM
from database import db
from jose import jwt, JWTError
from pydantic import ValidationError

def response(body, status=200):
    return {
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS, POST, GET, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    }

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "").upper()
    
    if method == "OPTIONS":
        return response({"message": "CORS OK"}, 200)
    
    body_data = args.get("body")
    if isinstance(body_data, str):
        body_data = json.loads(body_data)

    try:
        # REGISTER
        if path == "/register" and method == "POST":
            try:
                user = UserCreate(**body_data)
            except ValidationError as e:
                return response({"error": e.errors()}, 400)

            if db.users.find_one({"username": user.username}):
                return response({"detail": "Username already exists"}, 400)
            
            if db.users.find_one({"email": user.email}):
                return response({"detail": "Email already exists"}, 400)

            user_dict = user.dict()
            user_dict["password"] = hash_password(user_dict["password"])
            user_dict["role"] = "staff"

            result = db.users.insert_one(user_dict)
            return response({"message": "User registered successfully", "user_id": str(result.inserted_id)}, 201)

        # LOGIN
        elif path == "/login" and method == "POST":
            try:
                user_login = UserLogin(**body_data)
            except ValidationError as e:
                return response({"error": e.errors()}, 400)

            db_user = db.users.find_one({"username": user_login.username})
            if not db_user or not verify_password(user_login.password, db_user["password"]):
                return response({"detail": "Invalid credentials"}, 401)

            access_token = create_access_token(data={"sub": user_login.username})
            refresh_token = create_refresh_token(data={"sub": user_login.username})

            return response({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            })

        # REFRESH TOKEN
        elif path == "/token/refresh" and method == "POST":
            refresh_token_str = body_data.get("refresh")
            if not refresh_token_str:
                return response({"detail": "Missing refresh token"}, 400)

            try:
                payload = jwt.decode(refresh_token_str, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                if not username:
                    return response({"detail": "Invalid token"}, 401)
                
                access_token = create_access_token(data={"sub": username})
                return response({"access": access_token})
            except JWTError:
                return response({"detail": "Invalid refresh token"}, 401)

        # CHANGE PASSWORD
        elif path == "/change-password" and method == "PUT":
            username = body_data.get("username")
            curr_pass = body_data.get("current_password")
            new_pass = body_data.get("new_password")

            if not all([username, curr_pass, new_pass]):
                return response({"detail": "Missing fields"}, 400)

            user = db.users.find_one({"username": username})
            if not user:
                return response({"detail": "User not found"}, 404)

            if not verify_password(curr_pass, user["password"]):
                return response({"detail": "Current password is incorrect"}, 401)

            hashed_password = hash_password(new_pass)
            db.users.update_one(
                {"username": username},
                {"$set": {"password": hashed_password}}
            )
            return response({"message": "Password changed successfully"})

        # Health check
        elif path == "/health":
            try:
                db.command('ping')
                return response({"status": "healthy", "service": "auth", "database": "connected"})
            except Exception as e:
                return response({"status": "unhealthy", "error": str(e)}, 500)

        else:
            return response({"detail": f"Route {method} {path} not found"}, 404)

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return response({"detail": "Internal Server Error"}, 500)