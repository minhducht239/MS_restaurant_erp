from bson import ObjectId

def table_helper(table) -> dict:
    return {
        "id": str(table["_id"]),
        "number": table["number"],
        "status": table["status"],
        "location": table.get("location"),
        "type": table.get("type"),           # Loại bàn (thường, VIP, ngoài trời...)
        "seats": table.get("seats"),         # Số ghế
        "note": table.get("note"),           # Ghi chú
        "created_at": table.get("created_at"),
        "updated_at": table.get("updated_at"),
    }

def order_helper(order) -> dict:
    return {
        "id": str(order["_id"]),
        "table_id": str(order["table_id"]),
        "items": order.get("items", []),     # Danh sách món (chỉ lưu id, số lượng, giá, ...; chi tiết lấy từ menu service)
        "total": order.get("total"),         # Tổng tiền order
        "status": order.get("status"),       # Trạng thái order (đang gọi, đã thanh toán...)
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
    }