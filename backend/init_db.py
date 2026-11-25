#!/usr/bin/env python3
"""
ElectroRent AI - Database Initialization Script
Run this script to initialize the SQLite database with all tables and sample data.
"""
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import db, init_database

def main():
    """Initialize database and verify setup"""
    print("=" * 60)
    print("ElectroRent AI - Database Initialization")
    print("=" * 60)
    
    # Initialize database
    print("\n[1/2] Initializing database tables...")
    try:
        init_database()
        print("  ✓ Database tables created successfully")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 1
    
    # Verify setup
    print("\n[2/2] Verifying database setup...")
    try:
        # Check tables
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t['name'] for t in tables]
        print(f"  ✓ Tables: {', '.join(table_names)}")
        
        # Check categories
        categories = db.execute("SELECT COUNT(*) as count FROM categories")
        print(f"  ✓ Categories: {categories[0]['count']}")
        
        # Check products
        products = db.execute("SELECT COUNT(*) as count FROM products")
        print(f"  ✓ Products: {products[0]['count']}")
        
        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"  ✗ Verification error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())