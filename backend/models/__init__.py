"""
SQLAlchemy Database Models for ElectroRent AI
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, JSON, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.database import Base

class User(Base):
    """User authentication and basic info"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default='customer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    relationships
    customer = relationship("Customer", back_populates="user", uselist=False)
    rentals_created = relationship("Rental", back_populates="created_by_user")
    payments_processed = relationship("Payment", back_populates="processed_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Customer(Base):
    """Extended customer profile with analytics data"""
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    date_of_birth = Column(Date)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default='USA')
    id_type = Column(String(50))
    id_number = Column(String(50))
    credit_score = Column(Integer)
    total_rentals = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    average_rental_duration = Column(Float, default=0.0)
    late_returns_count = Column(Integer, default=0)
    customer_segment = Column(String(30), CheckConstraint("customer_segment IN ('new', 'regular', 'premium', 'vip')"))
    clv = Column(Float, default=0.0)  # Customer Lifetime Value
    last_rental_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="customer")
    rentals = relationship("Rental", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")
    activities = relationship("CustomerActivity", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")


class Category(Base):
    """Product categories"""
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(50))
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    """Electronic gadget inventory"""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    brand = Column(String(100))
    model_number = Column(String(100))
    image_url = Column(Text)
    specifications = Column(JSON, default=dict)
    daily_rate = Column(Float, nullable=False)
    weekly_rate = Column(Float)
    monthly_rate = Column(Float)
    deposit_amount = Column(Float, default=0.0)
    total_quantity = Column(Integer, default=1)
    available_quantity = Column(Integer, default=1, index=True)
    condition_status = Column(String(20), default='new')
    weight_kg = Column(Float)
    dimensions = Column(JSON, default=dict)
    purchase_price = Column(Float)
    purchase_date = Column(Date)
    depreciation_rate = Column(Float, default=10.0)
    maintenance_required = Column(Boolean, default=False)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    rentals = relationship("Rental", back_populates="product")
    inventory_transactions = relationship("InventoryTransaction", back_populates="product")
    pricing_history = relationship("PricingHistory", back_populates="product")
    demand_forecasts = relationship("DemandForecast", back_populates="product")
    pricing_recommendations = relationship("PricingRecommendation", back_populates="product")
    reviews = relationship("Review", back_populates="product")


class InventoryTransaction(Base):
    """Inventory movement tracking"""
    __tablename__ = "inventory_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    transaction_type = Column(String(20), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    notes = Column(Text)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    product = relationship("Product", back_populates="inventory_transactions")
    performer = relationship("User")


class Rental(Base):
    """Rental bookings"""
    __tablename__ = "rentals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rental_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    rental_start_date = Column(Date, nullable=False)
    rental_end_date = Column(Date, nullable=False)
    actual_return_date = Column(Date)
    rental_days = Column(Integer, nullable=False)
    daily_rate_at_booking = Column(Float, nullable=False)
    subtotal_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    deposit_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    deposit_status = Column(String(20), default='held')
    late_fee = Column(Float, default=0.0)
    damage_fee = Column(Float, default=0.0)
    status = Column(String(30), default='confirmed', index=True)
    cancellation_reason = Column(Text)
    customer_notes = Column(Text)
    staff_notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="rentals")
    product = relationship("Product", back_populates="rentals")
    created_by_user = relationship("User", back_populates="rentals_created")
    payments = relationship("Payment", back_populates="rental")
    extensions = relationship("RentalExtension", back_populates="rental")
    returns = relationship("Return", back_populates="rental")
    reviews = relationship("Review", back_populates="rental")


class RentalExtension(Base):
    """Rental period extensions"""
    __tablename__ = "rental_extensions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id", ondelete="CASCADE"), index=True)
    original_end_date = Column(Date, nullable=False)
    new_end_date = Column(Date, nullable=False)
    additional_days = Column(Integer, nullable=False)
    additional_amount = Column(Float, nullable=False)
    extension_reason = Column(Text)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rental = relationship("Rental", back_populates="extensions")


class Return(Base):
    """Product return records"""
    __tablename__ = "returns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id", ondelete="CASCADE"), index=True)
    actual_return_date = Column(DateTime, nullable=False)
    return_condition = Column(String(30))
    damage_description = Column(Text)
    late_return = Column(Boolean, default=False)
    late_fee_charged = Column(Float, default=0.0)
    damage_fee_charged = Column(Float, default=0.0)
    deposit_refunded = Column(Float, default=0.0)
    deposit_forfeited = Column(Float, default=0.0)
    inspection_notes = Column(Text)
    inspected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rental = relationship("Rental", back_populates="returns")


class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), unique=True, nullable=False)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)
    payment_type = Column(String(30), nullable=False)
    payment_method = Column(String(30), nullable=False)
    payment_status = Column(String(20), default='pending', index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    transaction_id = Column(String(255))
    payment_gateway_response = Column(JSON)
    receipt_url = Column(Text)
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rental = relationship("Rental", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")
    processed_by_user = relationship("User", back_populates="payments_processed")


class PricingHistory(Base):
    """Historical pricing changes"""
    __tablename__ = "pricing_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    previous_rate = Column(Float)
    new_rate = Column(Float)
    rate_type = Column(String(20))
    change_reason = Column(String(100))
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="pricing_history")


class CustomerActivity(Base):
    """Customer behavior tracking"""
    __tablename__ = "customer_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    activity_type = Column(String(50), nullable=False, index=True)
    activity_details = Column(JSONB, default=dict)
    session_id = Column(String(100))
    ip_address = Column(INET)
    user_agent = Column(Text)
    page_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    customer = relationship("Customer", back_populates="activities")


class Review(Base):
    """Product reviews"""
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(200))
    review_text = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    response_text = Column(Text)
    response_date = Column(Date)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    rental = relationship("Rental", back_populates="reviews")


class AnalyticsReport(Base):
    """Saved analytics reports"""
    __tablename__ = "analytics_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(String(50), nullable=False, index=True)
    report_period = Column(String(20))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    report_data = Column(JSONB, nullable=False)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class DemandForecast(Base):
    """ML demand predictions"""
    __tablename__ = "demand_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    forecast_period = Column(String(20))
    predicted_demand = Column(Integer, nullable=False)
    confidence_level = Column(Float)
    actual_demand = Column(Integer)
    model_version = Column(String(20))
    features_used = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="demand_forecasts")
    category = relationship("Category")


class PricingRecommendation(Base):
    """Dynamic pricing suggestions"""
    __tablename__ = "pricing_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    recommendation_date = Column(Date, nullable=False, index=True)
    current_rate = Column(Float)
    recommended_rate = Column(Float)
    min_rate = Column(Float)
    max_rate = Column(Float)
    demand_factor = Column(Float)
    competition_factor = Column(Float)
    seasonality_factor = Column(Float)
    confidence_score = Column(Float)
    recommendation_reason = Column(Text)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    applied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="pricing_recommendations")


class AuditLog(Base):
    """System audit trail"""
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    action_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="audit_logs")