from models import user_helper
from database import db
from schemas import UserUpdate, AvatarUploadResponse
from auth import get_user_from_request
import json
from pathlib import Path
import base64
import os

# File upload configuration
UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "get").lower()
    
    # Health check
    if path == "/health":
        try:
            db.command('ping')
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "healthy", "service": "user", "database": "connected"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "unhealthy", "error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Xác thực user
    user_token = get_user_from_request(args)
    if not user_token:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"}),
            "headers": {"Content-Type": "application/json"}
        }

    # GET /users/me - Lấy thông tin user hiện tại
    if path == "/users/me" and method == "get":
        try:
            user = db.users.find_one({"username": user_token["username"]})
            if not user:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "User not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            return {
                "statusCode": 200,
                "body": json.dumps(user_helper(user)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # PATCH /users/me - Cập nhật profile
    if path == "/users/me" and method == "patch":
        try:
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            if not data:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No data to update"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Check email uniqueness if updating email
            if data.get("email"):
                existing_user = db.users.find_one({
                    "email": data["email"],
                    "username": {"$ne": user_token["username"]}
                })
                if existing_user:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Email already in use"}),
                        "headers": {"Content-Type": "application/json"}
                    }
            
            update_data = {k: v for k, v in data.items() if v is not None and k != "username"}
            
            db.users.update_one(
                {"username": user_token["username"]},
                {"$set": update_data}
            )
            
            updated_user = db.users.find_one({"username": user_token["username"]})
            return {
                "statusCode": 200,
                "body": json.dumps(user_helper(updated_user)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # POST /users/upload-avatar - Upload avatar (base64)
    if path == "/users/upload-avatar" and method == "post":
        try:
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            if not data.get("file"):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No file provided"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Decode base64 image
            try:
                image_data = base64.b64decode(data["file"])
            except Exception:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid base64 data"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Validate file size (max 5MB)
            if len(image_data) > 5 * 1024 * 1024:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "File too large. Max 5MB allowed"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Get current user
            current_user = db.users.find_one({"username": user_token["username"]})
            if not current_user:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "User not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Delete old avatar if exists
            old_avatar = current_user.get("avatar")
            if old_avatar and not old_avatar.startswith("http"):
                old_file_path = Path(old_avatar.lstrip("/"))
                if old_file_path.exists():
                    old_file_path.unlink()
            
            # Save new avatar
            file_ext = data.get("file_ext", "jpg")
            filename = f"{user_token['username']}_avatar.{file_ext}"
            file_path = UPLOAD_DIR / filename
            
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # Update avatar path in database
            avatar_url = f"/uploads/avatars/{filename}"
            db.users.update_one(
                {"username": user_token["username"]},
                {"$set": {"avatar": avatar_url}}
            )
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "avatar": avatar_url,
                    "message": "Avatar uploaded successfully"
                }),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # DELETE /users/avatar - Xóa avatar
    if path == "/users/avatar" and method == "delete":
        try:
            current_user = db.users.find_one({"username": user_token["username"]})
            if not current_user:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "User not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            if not current_user.get("avatar"):
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "No avatar to delete"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Delete file if exists
            avatar_path = current_user["avatar"]
            if avatar_path and not avatar_path.startswith("http"):
                file_path = Path(avatar_path.lstrip("/"))
                if file_path.exists():
                    file_path.unlink()
            
            # Remove avatar from database
            db.users.update_one(
                {"username": user_token["username"]},
                {"$set": {"avatar": None}}
            )
            
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Avatar deleted successfully"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /users/list - Danh sách users (admin only)
    if path == "/users/list" and method == "get":
        try:
            current_user = db.users.find_one({"username": user_token["username"]})
            if not current_user or current_user.get("role") != "admin":
                return {
                    "statusCode": 403,
                    "body": json.dumps({"error": "Admin access required"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            skip = int(args.get("skip", 0))
            limit = int(args.get("limit", 10))
            
            users = list(db.users.find().skip(skip).limit(limit))
            results = [user_helper(u) for u in users]
            
            return {
                "statusCode": 200,
                "body": json.dumps(results),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /users/<username> - Lấy user theo username
    if path.startswith("/users/") and method == "get":
        username = path.split("/")[-1]
        try:
            current_user = db.users.find_one({"username": user_token["username"]})
            
            # Allow users to view their own profile or admin to view any profile
            if current_user["username"] != username and current_user.get("role") != "admin":
                return {
                    "statusCode": 403,
                    "body": json.dumps({"error": "Access denied"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            user = db.users.find_one({"username": username})
            if not user:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "User not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            return {
                "statusCode": 200,
                "body": json.dumps(user_helper(user)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Default: 404
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not found"}),
        "headers": {"Content-Type": "application/json"}
    }