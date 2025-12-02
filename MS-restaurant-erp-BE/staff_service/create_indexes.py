from database import db
from pymongo import ASCENDING, DESCENDING, TEXT
import asyncio

async def create_indexes():
    """Tạo indexes để tối ưu performance"""
    
    print("Creating indexes for staff collection...")
    
    try:
        # 1. Unique index cho phone
        await db.staff.create_index(
            [('phone', ASCENDING)],
            unique=True,
            name='idx_phone_unique'
        )
        print(" Created unique index on phone")
        
        # 2. Index cho role
        await db.staff.create_index(
            [('role', ASCENDING)],
            name='idx_role'
        )
        print(" Created index on role")
        
        # 3. Index cho hire_date
        await db.staff.create_index(
            [('hire_date', DESCENDING)],
            name='idx_hire_date'
        )
        print(" Created index on hire_date")
        
        # 4. Text index cho search
        await db.staff.create_index(
            [('name', TEXT), ('phone', TEXT)],
            name='idx_text_search'
        )
        print(" Created text index for search")
        
        # 5. Index cho salary
        await db.staff.create_index(
            [('salary', DESCENDING)],
            name='idx_salary'
        )
        print(" Created index on salary")
        
        # 6. Index cho created_at
        await db.staff.create_index(
            [('created_at', DESCENDING)],
            name='idx_created_at'
        )
        print(" Created index on created_at")
        
        # 7. Compound index cho role + hire_date
        await db.staff.create_index(
            [('role', ASCENDING), ('hire_date', DESCENDING)],
            name='idx_role_hire_date'
        )
        print(" Created compound index (role, hire_date)")
        
        print("\n All indexes created successfully!")
        
        # List all indexes
        indexes = await db.staff.list_indexes().to_list(None)
        print("\nList of created indexes:")
        for idx in indexes:
            print(f"  - {idx['name']}")
        
        return True
        
    except Exception as e:
        print(f"\n Error creating indexes: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(create_indexes())