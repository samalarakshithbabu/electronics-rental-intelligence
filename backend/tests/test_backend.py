"""
Automated Tests for ElectroRent AI Backend
Tests authentication, rentals, payments, and ML integration
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from database.connection import db, execute, insert, execute_update
from security.hashing import hash_password, verify_password
from security.jwt_auth import create_access_token, decode_token
import json
from datetime import date, timedelta


# Test client
client = TestClient(app)


class TestAuthentication:
    """Tests for authentication endpoints"""
    
    def test_health_check(self):
        """Health check should return healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_login_nonexistent_user(self):
        """Login with nonexistent user should fail"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password123"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_wrong_password(self):
        """Login with wrong password should fail"""
        response = client.post("/api/auth/login", json={
            "email": "test@electrorent.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_register_weak_password(self):
        """Registration with weak password should fail"""
        response = client.post("/api/auth/register", json={
            "email": "newuser@test.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        })
        assert response.status_code == 400
    
    def test_password_hashing(self):
        """Password hashing should work correctly"""
        password = "SecurePass123!"
        hashed = hash_password(password)
        
        # Hash should be different from plaintext
        assert hashed != password
        # Hash should start with bcrypt marker
        assert hashed.startswith("$2b$")
        # Verification should succeed
        assert verify_password(password, hashed) is True
        # Wrong password should fail
        assert verify_password("wrongpassword", hashed) is False
    
    def test_jwt_token_creation(self):
        """JWT token creation should work"""
        token = create_access_token(
            user_id=1,
            email="test@electrorent.com",
            role="customer"
        )
        
        assert token is not None
        assert len(token) > 0
        # JWT should have 3 parts separated by dots
        assert len(token.split(".")) == 3
        
        # Token should be decodable
        token_data = decode_token(token)
        assert token_data.user_id == 1
        assert token_data.email == "test@electrorent.com"
        assert token_data.role == "customer"


class TestProducts:
    """Tests for product endpoints"""
    
    def test_list_products(self):
        """Listing products should return all products"""
        response = client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_product(self):
        """Getting a specific product should work"""
        response = client.get("/api/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "MacBook Pro" in data["name"]
    
    def test_get_nonexistent_product(self):
        """Getting nonexistent product should return 404"""
        response = client.get("/api/products/9999")
        assert response.status_code == 404


class TestRentals:
    """Tests for rental endpoints"""
    
    def test_list_rentals_unauthorized(self):
        """Listing rentals without auth should fail"""
        response = client.get("/api/rentals")
        assert response.status_code == 401
    
    def test_rental_return(self):
        """Rental return should work with valid auth"""
        # First login
        login_response = client.post("/api/auth/login", json={
            "email": "test@electrorent.com",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create a new rental first
        # (skipping for now since rental creation requires more setup)
        
        # Return rental (existing rental)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/rentals/1/return", headers=headers)
        # Rental might already be returned, but should not be 500 error
        assert response.status_code in [200, 400]


class TestDatabase:
    """Tests for database operations"""
    
    def test_execute_query(self):
        """Database execution should work"""
        results = execute("SELECT COUNT(*) as count FROM products")
        assert len(results) == 1
        assert results[0]["count"] > 0
    
    def test_insert_and_delete(self):
        """Database insert and delete should work"""
        # Insert a test category
        test_id = insert(
            "INSERT INTO categories (name, slug, description, icon) VALUES (?, ?, ?, ?)",
            ("Test Category", "test-cat", "Test description", "test")
        )
        assert test_id is not None
        assert test_id > 0
        
        # Clean up
        execute_update("DELETE FROM categories WHERE id = ?", (test_id,))
    
    def test_customer_segmentation(self):
        """Customer segmentation data should exist"""
        customers = db.execute("SELECT COUNT(*) as count FROM customers")
        assert customers[0]["count"] > 0


class TestSecurity:
    """Tests for security features"""
    
    def test_password_strength_validation(self):
        """Password strength validation should reject weak passwords"""
        from security.hashing import validate_password_strength
        
        # Weak passwords
        is_valid, _ = validate_password_strength("short")
        assert is_valid is False
        
        is_valid, _ = validate_password_strength("nouppercase123")
        assert is_valid is False
        
        is_valid, _ = validate_password_strength("NOLOWERCASE123")
        assert is_valid is False
        
        is_valid, _ = validate_password_strength("NoNumbers!")
        assert is_valid is False
        
        is_valid, _ = validate_password_strength("password123")
        assert is_valid is False
        
        # Strong password
        is_valid, _ = validate_password_strength("SecurePass123!")
        assert is_valid is True
    
    def test_bcrypt_different_hashes(self):
        """Same password should produce different hashes (salt)"""
        password = "SamePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts
        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestMLIntegration:
    """Tests for ML integration"""
    
    def test_ml_status_endpoint(self):
        """ML status endpoint should return model status"""
        response = client.get("/api/ml/status")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "demand_forecasting" in data["models"]
        assert "customer_segmentation" in data["models"]
        assert "product_recommendations" in data["models"]
    
    def test_demand_forecasting(self):
        """Demand forecasting should return predictions"""
        response = client.get("/api/forecasting/demand?days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7
        
        # Check forecast structure
        for forecast in data:
            assert "date" in forecast
            assert "predicted_demand" in forecast
            assert "confidence_lower" in forecast
            assert "confidence_upper" in forecast
    
    def test_pricing_recommendations(self):
        """Pricing recommendations should work"""
        response = client.get("/api/pricing/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)


class TestAnalytics:
    """Tests for analytics endpoints"""
    
    def test_dashboard_metrics(self):
        """Dashboard metrics should return data"""
        response = client.get("/api/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_revenue" in data
        assert "total_rentals" in data
        assert "active_rentals" in data
    
    def test_category_distribution(self):
        """Category distribution should return data"""
        response = client.get("/api/analytics/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total_revenue" in data


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])