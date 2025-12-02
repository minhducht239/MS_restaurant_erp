from database import db
from pymongo import ASCENDING, DESCENDING

def create_indexes():
    """Tạo indexes để tối ưu performance"""
    
    print("Creating indexes for tables collection...")
    
    try:
        db.tables.create_index([('name', ASCENDING)], unique=True, name='idx_name_unique')
        print("Created unique index on name")
        
        db.tables.create_index([('status', ASCENDING)], name='idx_status')
        print("Created index on status")
        
        db.tables.create_index([('floor', ASCENDING)], name='idx_floor')
        print("Created index on floor")
        
        db.tables.create_index(
            [('floor', ASCENDING), ('name', ASCENDING)],
            name='idx_floor_name'
        )
        print("Created compound index on floor and name")
        
        print("\nCreating indexes for orders collection...")
        
        db.orders.create_index([('table_id', ASCENDING)], name='idx_table_id')
        print("Created index on table_id")
        
        db.orders.create_index([('is_completed', ASCENDING)], name='idx_is_completed')
        print("Created index on is_completed")
        
        db.orders.create_index(
            [('table_id', ASCENDING), ('is_completed', ASCENDING)],
            name='idx_table_completed'
        )
        print("Created compound index on table_id and is_completed")
        
        db.orders.create_index([('created_at', DESCENDING)], name='idx_created_at')
        print("Created index on created_at")
        
        print("\nAll indexes created successfully")
        return True
        
    except Exception as e:
        print(f"Error creating indexes: {str(e)}")
        return False

if __name__ == "__main__":
    create_indexes()