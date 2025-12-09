from bson import ObjectId

ROLE_MAPPING = {
    'manager': 'Quản lý',
    'cashier': 'Thu ngân',
    'chef': 'Đầu bếp',
    'waiter': 'Phục vụ',
    'janitor': 'Vệ sinh',
}

def staff_helper(staff) -> dict:
    return {
        "id": str(staff["_id"]),
        "name": staff["name"],
        "phone": staff["phone"],
        "role": staff["role"],
        "role_display": ROLE_MAPPING.get(staff["role"], staff["role"]),
        "salary": str(staff["salary"]),
        "hire_date": staff["hire_date"].isoformat() if hasattr(staff["hire_date"], 'isoformat') else str(staff["hire_date"]),
        "created_at": staff.get("created_at"),
        "updated_at": staff.get("updated_at"),
    }