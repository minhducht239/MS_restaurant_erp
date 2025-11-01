from bson import ObjectId

def staff_helper(staff) -> dict:
    return {
        "id": str(staff["_id"]),
        "name": staff["name"],
        "phone": staff["phone"],
        "role": staff["role"],
        "salary": float(staff["salary"]),
        "hire_date": staff["hire_date"],
        "created_at": staff.get("created_at"),
        "updated_at": staff.get("updated_at"),
    }