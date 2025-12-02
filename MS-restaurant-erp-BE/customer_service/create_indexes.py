from database import db
from pymongo import ASCENDING, DESCENDING, TEXT

def create_indexes():
    """Tạo indexes để tối ưu performance cho Customer Service"""
    
    print("Creating indexes for customers collection...")
    
    try:
        # 1. Unique index cho phone
        db.customers.create_index(
            [('phone', ASCENDING)],
            unique=True,
            name='idx_phone_unique'
        )
        print(" Created unique index on phone")
        
        # 2. Index cho search
        db.customers.create_index(
            [('name', ASCENDING), ('phone', ASCENDING)],
            name='idx_search_fields'
        )
        print(" Created index for search (name, phone)")
        
        # 3. Text index cho full-text search
        db.customers.create_index(
            [('name', TEXT), ('phone', TEXT)],
            name='idx_text_search'
        )
        print(" Created text index for full-text search")
        
        # 4. Index cho sorting by loyalty_points
        db.customers.create_index(
            [('loyalty_points', DESCENDING)],
            name='idx_loyalty_desc'
        )
        print(" Created index on loyalty_points (desc)")
        
        # 5. Index cho sorting by total_spent
        db.customers.create_index(
            [('total_spent', DESCENDING)],
            name='idx_spent_desc'
        )
        print(" Created index on total_spent (desc)")
        
        # 6. Index cho date filtering
        db.customers.create_index(
            [('created_at', DESCENDING)],
            name='idx_created_date'
        )
        print(" Created index on created_at (desc)")
        
        # 7. Index cho last_visit
        db.customers.create_index(
            [('last_visit', DESCENDING)],
            name='idx_last_visit'
        )
        print(" Created index on last_visit (desc)")
        
        # 8. Compound index cho loyalty_points và total_spent
        db.customers.create_index(
            [('loyalty_points', DESCENDING), ('total_spent', DESCENDING)],
            name='idx_loyalty_spent'
        )
        print(" Created compound index (loyalty_points, total_spent)")
        
        # 9. Compound index cho date range queries
        db.customers.create_index(
            [('created_at', ASCENDING), ('last_visit', ASCENDING)],
            name='idx_dates'
        )
        print(" Created compound index (created_at, last_visit)")
        
        # 10. Index cho visit_count
        db.customers.create_index(
            [('visit_count', DESCENDING)],
            name='idx_visit_count'
        )
        print(" Created index on visit_count (desc)")
        
        print("\n All indexes created successfully!")
        
        # List all indexes
        indexes = db.customers.list_indexes()
        print("\nList of created indexes:")
        for idx in indexes:
            print(f"  - {idx['name']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating indexes: {str(e)}")
        return False

if __name__ == "__main__":
    create_indexes()