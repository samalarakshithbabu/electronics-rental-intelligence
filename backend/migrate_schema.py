"""
Database Migration Script
Adds missing columns to the rentals table
"""
from database.connection import db, execute

def migrate():
    """Run database migrations"""
    print("Running database migrations...")
    
    # Check if column exists
    columns = db.execute_one("PRAGMA table_info(rentals)")
    if columns is None:
        print("Rentals table not found")
        return
    
    # Get all columns
    all_columns = db.execute("PRAGMA table_info(rentals)")
    column_names = [c['name'] for c in all_columns]
    
    migrations = [
        ("actual_return_date", "DATE"),
        ("is_overdue", "INTEGER DEFAULT 0"),
        ("late_fee", "REAL DEFAULT 0.0"),
    ]
    
    for column_name, column_type in migrations:
        if column_name not in column_names:
            try:
                db.execute_update(f"ALTER TABLE rentals ADD COLUMN {column_name} {column_type}")
                print(f"  ✓ Added column: {column_name}")
            except Exception as e:
                print(f"  ✗ Error adding {column_name}: {e}")
        else:
            print(f"  ✓ Column {column_name} already exists")
    
    print("Migrations complete!")

if __name__ == "__main__":
    migrate()