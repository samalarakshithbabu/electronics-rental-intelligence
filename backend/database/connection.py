"""
AI-Powered Electronics Rental and Revenue Intelligence - Database Connection Manager
Supports PostgreSQL with SQLite fallback for development
"""
import os
import sqlite3
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database configuration - use absolute path for SQLite
DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DB_DIR, "AI-Powered Electronics Rental.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
USE_POSTGRES = DATABASE_URL.startswith("postgresql")

# Try to import PostgreSQL drivers
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Thread-local storage for connections
_local = threading.local()


def get_connection():
    """Get a database connection (request-scoped for SQLite)"""
    if USE_POSTGRES and POSTGRES_AVAILABLE:
        return _get_postgres_connection()
    else:
        return _get_sqlite_connection()


def _get_postgres_connection():
    """Get PostgreSQL connection"""
    if not POSTGRES_AVAILABLE:
        raise RuntimeError("PostgreSQL driver not available")
    
    if not hasattr(_local, 'connection') or _local.connection is None or _local.connection.closed:
        _local.connection = psycopg2.connect(
            DATABASE_URL.replace("postgresql://", ""),
            cursor_factory=RealDictCursor
        )
    return _local.connection


def _get_sqlite_connection():
    """Get SQLite connection (thread-safe)"""
    if not hasattr(_local, 'connection') or _local.connection is None:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.isolation_level = None  # Autocommit mode
        _local.connection = conn
    return _local.connection


def close_connection():
    """Close the thread-local connection"""
    if hasattr(_local, 'connection') and _local.connection:
        try:
            _local.connection.close()
        except:
            pass
        _local.connection = None


def execute(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute query and return results"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if cursor.description:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        return []
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()


def execute_one(query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    """Execute query and return single result"""
    results = execute(query, params)
    return results[0] if results else None


def execute_update(query: str, params: tuple = None) -> int:
    """Execute update/insert/delete and return row count"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()


def insert(query: str, params: tuple = None) -> int:
    """Insert record and return ID"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()


# Global database manager instance (legacy, for backward compatibility)
class DatabaseManager:
    """Database connection and operations manager - legacy wrapper"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return get_connection()
    
    @property
    def connection(self):
        """Get current connection, create if needed"""
        return get_connection()
    
    def execute(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        return execute(query, params)
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        return execute_one(query, params)
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        return execute_update(query, params)
    
    def insert(self, query: str, params: tuple = None) -> int:
        return insert(query, params)
    
    def close(self):
        close_connection()


# Global db instance for backward compatibility
db = DatabaseManager()


def init_database():
    """Initialize database tables"""
    logger.info("Initializing database...")
    
    # Create tables
    queries = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            role VARCHAR(20) DEFAULT 'customer',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            total_rentals INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0.0,
            customer_segment VARCHAR(30) DEFAULT 'new',
            clv REAL DEFAULT 0.0,
            last_rental_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            slug VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            icon VARCHAR(50),
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category_id INTEGER REFERENCES categories(id),
            brand VARCHAR(100),
            image_url TEXT,
            daily_rate REAL NOT NULL,
            total_quantity INTEGER DEFAULT 1,
            available_quantity INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_number VARCHAR(50) UNIQUE NOT NULL,
            customer_id INTEGER REFERENCES customers(id),
            product_id INTEGER REFERENCES products(id),
            rental_start_date DATE NOT NULL,
            rental_end_date DATE NOT NULL,
            rental_days INTEGER NOT NULL,
            daily_rate REAL NOT NULL,
            total_amount REAL NOT NULL,
            status VARCHAR(30) DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_number VARCHAR(50) UNIQUE NOT NULL,
            rental_id INTEGER REFERENCES rentals(id),
            customer_id INTEGER REFERENCES customers(id),
            payment_type VARCHAR(30) NOT NULL,
            payment_method VARCHAR(30) NOT NULL,
            payment_status VARCHAR(20) DEFAULT 'pending',
            amount REAL NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS demand_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            forecast_date DATE NOT NULL,
            predicted_demand REAL NOT NULL,
            confidence_lower REAL,
            confidence_upper REAL,
            model_version VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    for query in queries:
        try:
            db.execute_update(query)
        except Exception as e:
            logger.warning(f"Table creation warning: {e}")
    
    # Insert sample data if tables are empty
    _insert_sample_data()
    
    logger.info("Database initialized successfully")


def _insert_sample_data():
    """Insert sample data for demonstration"""
    try:
        # Check if data exists
        count = db.execute_one("SELECT COUNT(*) as count FROM categories")
        if count and count['count'] > 0:
            return
        
        # Insert categories
        categories = [
            ('Laptops', 'laptops', 'High-performance laptops', 'laptop'),
            ('Cameras', 'cameras', 'Professional cameras', 'camera'),
            ('Audio Equipment', 'audio', 'High-quality audio gear', 'headphones'),
            ('Gaming', 'gaming', 'Gaming consoles', 'gamepad-2'),
            ('Smart Home', 'smart-home', 'Smart devices', 'home'),
            ('Tablets', 'tablets', 'Portable tablets', 'tablet')
        ]
        
        for cat in categories:
            try:
                db.insert(
                    "INSERT INTO categories (name, slug, description, icon) VALUES (?, ?, ?, ?)",
                    cat
                )
            except:
                pass
        
        # Insert products
        products = [
            ('MBP-16-001', 'MacBook Pro 16"', 'laptops', 'Apple', 45),
            ('DX-15-001', 'Dell XPS 15', 'laptops', 'Dell', 35),
            ('SA7-III-001', 'Sony Alpha A7 III', 'cameras', 'Sony', 40),
            ('CE-R5-001', 'Canon EOS R5', 'cameras', 'Canon', 50),
            ('XM5-001', 'Sony WH-1000XM5', 'audio', 'Sony', 15),
            ('PS5-001', 'PlayStation 5', 'gaming', 'Sony', 25),
            ('XSX-001', 'Xbox Series X', 'gaming', 'Microsoft', 22),
            ('IPAD-001', 'iPad Pro 12.9"', 'tablets', 'Apple', 30)
        ]
        
        for prod in products:
            sku, name, cat_slug, brand, rate = prod
            cat_result = db.execute_one("SELECT id FROM categories WHERE slug = ?", (cat_slug,))
            if cat_result:
                try:
                    db.insert(
                        "INSERT INTO products (sku, name, category_id, brand, daily_rate, total_quantity, available_quantity) VALUES (?, ?, ?, ?, ?, 5, ?)",
                        (sku, name, cat_result['id'], brand, rate, rate)
                    )
                except:
                    pass
        
        logger.info("Sample data inserted successfully")
    except Exception as e:
        logger.warning(f"Sample data insertion warning: {e}")


# Convenience functions for common operations
def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    return db.execute_one("SELECT * FROM users WHERE email = ?", (email,))


def create_user(email: str, password_hash: str, first_name: str, last_name: str) -> int:
    """Create new user and return ID"""
    return db.insert(
        "INSERT INTO users (email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?)",
        (email, password_hash, first_name, last_name)
    )


def get_all_products(category: str = None, available: bool = True) -> List[Dict[str, Any]]:
    """Get all products with optional filters"""
    query = """
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_active = 1
    """
    params = []
    
    if category:
        query += " AND c.slug = ?"
        params.append(category)
    
    if available:
        query += " AND p.available_quantity > 0"
    
    return db.execute(query, tuple(params) if params else None)


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Get product by ID"""
    return db.execute_one(
        "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = ?",
        (product_id,)
    )


def create_rental(customer_id: int, product_id: int, start_date: str, end_date: str, days: int, daily_rate: float, total_amount: float) -> int:
    """Create new rental and return ID"""
    import uuid
    rental_number = f"RN-{uuid.uuid4().hex[:8].upper()}"
    
    # Update product availability
    db.execute_update("UPDATE products SET available_quantity = available_quantity - 1 WHERE id = ?", (product_id,))
    
    return db.insert(
        "INSERT INTO rentals (rental_number, customer_id, product_id, rental_start_date, rental_end_date, rental_days, daily_rate, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (rental_number, customer_id, product_id, start_date, end_date, days, daily_rate, total_amount)
    )


def get_rentals_by_customer(customer_id: int) -> List[Dict[str, Any]]:
    """Get all rentals for a customer"""
    return db.execute(
        "SELECT r.*, p.name as product_name, c.name as category_name FROM rentals r LEFT JOIN products p ON r.product_id = p.id LEFT JOIN categories c ON p.category_id = c.id WHERE r.customer_id = ? ORDER BY r.created_at DESC",
        (customer_id,)
    )


def get_all_rentals() -> List[Dict[str, Any]]:
    """Get all rentals"""
    return db.execute(
        "SELECT r.*, p.name as product_name FROM rentals r LEFT JOIN products p ON r.product_id = p.id ORDER BY r.created_at DESC"
    )


def get_rental_by_id(rental_id: int) -> Optional[Dict[str, Any]]:
    """Get rental by ID"""
    return db.execute_one(
        "SELECT r.*, p.name as product_name FROM rentals r LEFT JOIN products p ON r.product_id = p.id WHERE r.id = ?",
        (rental_id,)
    )


def update_rental(rental_id: int, updates: Dict[str, Any]) -> bool:
    """Update rental record"""
    if not updates:
        return False
    
    set_clauses = []
    params = []
    for key, value in updates.items():
        set_clauses.append(f"{key} = ?")
        params.append(value)
    
    params.append(rental_id)
    
    query = f"UPDATE rentals SET {', '.join(set_clauses)} WHERE id = ?"
    return db.execute_update(query, tuple(params)) > 0


def create_payment(rental_id: int, customer_id: int, payment_type: str, payment_method: str, amount: float) -> int:
    """Create payment record"""
    import uuid
    payment_number = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    
    return db.insert(
        "INSERT INTO payments (payment_number, rental_id, customer_id, payment_type, payment_method, amount, payment_status) VALUES (?, ?, ?, ?, ?, ?, 'completed')",
        (payment_number, rental_id, customer_id, payment_type, payment_method, amount)
    )


def get_dashboard_metrics() -> Dict[str, Any]:
    """Get dashboard metrics from database"""
    total_revenue = db.execute_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_status = 'completed'")
    total_rentals = db.execute_one("SELECT COUNT(*) as count FROM rentals")
    active_rentals = db.execute_one("SELECT COUNT(*) as count FROM rentals WHERE status IN ('confirmed', 'in_progress')")
    overdue_rentals = db.execute_one("SELECT COUNT(*) as count FROM rentals WHERE status = 'overdue'")
    available_items = db.execute_one("SELECT SUM(available_quantity) as total FROM products WHERE is_active = 1")
    
    return {
        "total_revenue": total_revenue['total'] if total_revenue else 0,
        "total_rentals": total_rentals['count'] if total_rentals else 0,
        "active_rentals": active_rentals['count'] if active_rentals else 0,
        "available_items": available_items['total'] if available_items else 0,
        "overdue_rentals": overdue_rentals['count'] if overdue_rentals else 0,
        "revenue_growth": 12.5
    }


def get_revenue_analytics(period: str = "monthly") -> Dict[str, Any]:
    """Get revenue analytics"""
    revenue_data = db.execute(
        "SELECT strftime('%Y-%m', processed_at) as month, SUM(amount) as revenue, COUNT(*) as rentals FROM payments WHERE payment_status = 'completed' GROUP BY month ORDER BY month DESC LIMIT 12"
    )
    
    return {
        "period": period,
        "total_revenue": sum(r['revenue'] for r in revenue_data) if revenue_data else 0,
        "monthly_breakdown": revenue_data[::-1] if revenue_data else [],
        "avg_monthly_revenue": (sum(r['revenue'] for r in revenue_data) / len(revenue_data)) if revenue_data else 0
    }


def get_product_analytics() -> Dict[str, Any]:
    """Get product utilization analytics"""
    analytics = db.execute("""
        SELECT p.id as product_id, p.name, COUNT(r.id) as total_rentals, 
               COALESCE(SUM(r.rental_days), 0) as total_rental_days,
               COALESCE(SUM(r.total_amount), 0) as total_revenue,
               p.available_quantity
        FROM products p LEFT JOIN rentals r ON p.id = r.product_id
        WHERE p.is_active = 1
        GROUP BY p.id
    """)
    
    for item in analytics:
        total_days = item['total_rental_days']
        item['utilization_rate'] = round((total_days / 365) * 100, 2) if total_days > 0 else 0
    
    analytics_sorted = sorted(analytics, key=lambda x: x['utilization_rate'], reverse=True)
    avg_util = sum(a['utilization_rate'] for a in analytics) / len(analytics) if analytics else 0
    
    return {
        "products": analytics_sorted,
        "avg_utilization": round(avg_util, 2)
    }


def get_category_distribution() -> Dict[str, Any]:
    """Get revenue by category"""
    category_data = db.execute("""
        SELECT c.name, COALESCE(SUM(r.total_amount), 0) as revenue
        FROM categories c LEFT JOIN products p ON c.id = p.category_id
        LEFT JOIN rentals r ON p.id = r.product_id
        WHERE c.is_active = 1
        GROUP BY c.id
    """)
    
    if not category_data:
        return {
            "categories": [
                {"name": "Laptops", "value": 35, "color": "#6366f1", "revenue": 15000},
                {"name": "Cameras", "value": 25, "color": "#8b5cf6", "revenue": 10700},
                {"name": "Audio", "value": 15, "color": "#ec4899", "revenue": 6420},
                {"name": "Gaming", "value": 15, "color": "#f59e0b", "revenue": 6420},
                {"name": "Tablets", "value": 10, "color": "#10b981", "revenue": 4280}
            ],
            "total_revenue": 43620
        }
    
    total_revenue = sum(c['revenue'] for c in category_data)
    colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"]
    
    categories = []
    for i, cat in enumerate(category_data):
        categories.append({
            "name": cat['name'],
            "value": round((cat['revenue'] / total_revenue) * 100, 1) if total_revenue > 0 else 0,
            "color": colors[i % len(colors)],
            "revenue": round(cat['revenue'], 2)
        })
    
    return {
        "categories": categories,
        "total_revenue": round(total_revenue, 2)
    }


def save_demand_forecast(forecast_date: str, predicted_demand: float, confidence_lower: float, confidence_upper: float, model_version: str):
    """Save demand forecast to database"""
    db.execute_update(
        "INSERT INTO demand_forecasts (forecast_date, predicted_demand, confidence_lower, confidence_upper, model_version) VALUES (?, ?, ?, ?, ?)",
        (forecast_date, predicted_demand, confidence_lower, confidence_upper, model_version)
    )


def get_latest_demand_forecasts(days: int = 14) -> List[Dict[str, Any]]:
    """Get latest demand forecasts"""
    forecasts = db.execute(
        f"SELECT * FROM demand_forecasts ORDER BY forecast_date DESC LIMIT {days}"
    )
    return forecasts if forecasts else []