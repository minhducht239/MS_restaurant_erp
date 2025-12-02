from database import db
from pymongo import ASCENDING, DESCENDING, TEXT
import asyncio

async def create_indexes():
    """Tạo indexes để tối ưu performance"""
    
    print("Creating indexes for menu_items collection...")
    
    try:
        # 1. Index cho category
        await db.menu_items.create_index(
            [('category', ASCENDING)],
            name='idx_category'
        )
        print(" Created index on category")
        
        # 2. Index cho is_available
        await db.menu_items.create_index(
            [('is_available', ASCENDING)],
            name='idx_available'
        )
        print(" Created index on is_available")
        
        # 3. Text index cho search
        await db.menu_items.create_index(
            [('name', TEXT), ('description', TEXT)],
            name='idx_text_search'
        )
        print(" Created text index for search")
        
        # 4. Index cho sorting by name
        await db.menu_items.create_index(
            [('name', ASCENDING)],
            name='idx_name'
        )
        print(" Created index on name")
        
        # 5. Index cho sorting by price
        await db.menu_items.create_index(
            [('price', ASCENDING)],
            name='idx_price'
        )
        print(" Created index on price")
        
        # 6. Index cho created_at
        await db.menu_items.create_index(
            [('created_at', DESCENDING)],
            name='idx_created_at'
        )
        print(" Created index on created_at")
        
        # 7. Compound index cho category + available
        await db.menu_items.create_index(
            [('category', ASCENDING), ('is_available', ASCENDING)],
            name='idx_category_available'
        )
        print(" Created compound index (category, is_available)")
        
        print("\n All indexes created successfully!")
        
        # List all indexes
        indexes = await db.menu_items.list_indexes().to_list(None)
        print("\nList of created indexes:")
        for idx in indexes:
            print(f"  - {idx['name']}")
        
        return True
        
    except Exception as e:
        print(f"\n Error creating indexes: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(create_indexes())