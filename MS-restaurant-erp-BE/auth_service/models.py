def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role"),
        "avatar": user.get("avatar"),
        "phone": user.get("phone"),
    }