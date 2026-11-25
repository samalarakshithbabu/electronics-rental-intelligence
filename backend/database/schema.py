"""
ElectroRent AI - PostgreSQL Database Schema
Production-ready relational database for electronic gadget rental platform
"""

SCHEMA = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('customer', 'admin', 'staff')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- CUSTOMERS (Extended User Profile)
-- ============================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    id_type VARCHAR(50),
    id_number VARCHAR(50),
    credit_score INTEGER,
    total_rentals INTEGER DEFAULT 0,
    total_spent DECIMAL(12, 2) DEFAULT 0.0,
    average_rental_duration DECIMAL(5, 2) DEFAULT 0.0,
    late_returns_count INTEGER DEFAULT 0,
    customer_segment VARCHAR(30) CHECK (customer_segment IN ('new', 'regular', 'premium', 'vip')),
    clv DECIMAL(12, 2) DEFAULT 0.0, -- Customer Lifetime Value
    last_rental_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_user_id ON customers(user_id);
CREATE INDEX idx_customers_segment ON customers(customer_segment);

-- ============================================
-- CATEGORIES
-- ============================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    parent_category_id UUID REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent ON categories(parent_category_id);

-- ============================================
-- PRODUCTS
-- ============================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    brand VARCHAR(100),
    model_number VARCHAR(100),
    image_url TEXT,
    specifications JSONB DEFAULT '{}',
    daily_rate DECIMAL(10, 2) NOT NULL,
    weekly_rate DECIMAL(10, 2),
    monthly_rate DECIMAL(10, 2),
    deposit_amount DECIMAL(10, 2) DEFAULT 0.0,
    total_quantity INTEGER DEFAULT 1,
    available_quantity INTEGER DEFAULT 1,
    condition_status VARCHAR(20) DEFAULT 'new' CHECK (condition_status IN ('new', 'excellent', 'good', 'fair', 'needs_repair')),
    weight_kg DECIMAL(6, 3),
    dimensions JSONB DEFAULT '{}',
    purchase_price DECIMAL(12, 2),
    purchase_date DATE,
    depreciation_rate DECIMAL(5, 2) DEFAULT 10.0,
    maintenance_required BOOLEAN DEFAULT FALSE,
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_daily_rate ON products(daily_rate);
CREATE INDEX idx_products_available ON products(available_quantity);
CREATE INDEX idx_products_active ON products(is_active);

-- ============================================
-- INVENTORY TRANSACTIONS
-- ============================================

CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'rental_out', 'return', 'maintenance', 'disposal', 'adjustment')),
    quantity_change INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    reference_id UUID, -- Links to rental ID if applicable
    notes TEXT,
    performed_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_product ON inventory_transactions(product_id);
CREATE INDEX idx_inventory_date ON inventory_transactions(created_at);

-- ============================================
-- RENTALS
-- ============================================

CREATE TABLE rentals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rental_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    rental_start_date DATE NOT NULL,
    rental_end_date DATE NOT NULL,
    actual_return_date DATE,
    rental_days INTEGER NOT NULL,
    daily_rate_at_booking DECIMAL(10, 2) NOT NULL,
    subtotal_amount DECIMAL(12, 2) NOT NULL,
    discount_amount DECIMAL(12, 2) DEFAULT 0.0,
    tax_amount DECIMAL(12, 2) DEFAULT 0.0,
    deposit_amount DECIMAL(12, 2) DEFAULT 0.0,
    total_amount DECIMAL(12, 2) NOT NULL,
    deposit_status VARCHAR(20) DEFAULT 'held' CHECK (deposit_status IN ('held', 'refunded', 'forfeited')),
    late_fee DECIMAL(10, 2) DEFAULT 0.0,
    damage_fee DECIMAL(10, 2) DEFAULT 0.0,
    status VARCHAR(30) DEFAULT 'confirmed' CHECK (status IN ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'overdue', 'disputed')),
    cancellation_reason TEXT,
    customer_notes TEXT,
    staff_notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rentals_rental_number ON rentals(rental_number);
CREATE INDEX idx_rentals_customer ON rentals(customer_id);
CREATE INDEX idx_rentals_product ON rentals(product_id);
CREATE INDEX idx_rentals_dates ON rentals(rental_start_date, rental_end_date);
CREATE INDEX idx_rentals_status ON rentals(status);

-- ============================================
-- RENTAL EXTENSIONS
-- ============================================

CREATE TABLE rental_extensions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rental_id UUID REFERENCES rentals(id) ON DELETE CASCADE,
    original_end_date DATE NOT NULL,
    new_end_date DATE NOT NULL,
    additional_days INTEGER NOT NULL,
    additional_amount DECIMAL(10, 2) NOT NULL,
    extension_reason TEXT,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_extensions_rental ON rental_extensions(rental_id);

-- ============================================
-- RETURNS
-- ============================================

CREATE TABLE returns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rental_id UUID REFERENCES rentals(id) ON DELETE CASCADE,
    actual_return_date TIMESTAMP NOT NULL,
    return_condition VARCHAR(30) CHECK (return_condition IN ('excellent', 'good', 'fair', 'damaged', 'lost')),
    damage_description TEXT,
    late_return BOOLEAN DEFAULT FALSE,
    late_fee_charged DECIMAL(10, 2) DEFAULT 0.0,
    damage_fee_charged DECIMAL(10, 2) DEFAULT 0.0,
    deposit_refunded DECIMAL(10, 2) DEFAULT 0.0,
    deposit_forfeited DECIMAL(10, 2) DEFAULT 0.0,
    inspection_notes TEXT,
    inspected_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_returns_rental ON returns(rental_id);

-- ============================================
-- PAYMENTS
-- ============================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    rental_id UUID REFERENCES rentals(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    payment_type VARCHAR(30) NOT NULL CHECK (payment_type IN ('rental', 'deposit', 'late_fee', 'damage_fee', 'refund', 'extension')),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('credit_card', 'debit_card', 'cash', 'bank_transfer', 'paypal', 'other')),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled')),
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_id VARCHAR(255),
    payment_gateway_response JSONB,
    receipt_url TEXT,
    processed_by UUID REFERENCES users(id),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_rental ON payments(rental_id);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_status ON payments(payment_status);

-- ============================================
-- PRICING HISTORY
-- ============================================

CREATE TABLE pricing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    previous_rate DECIMAL(10, 2),
    new_rate DECIMAL(10, 2),
    rate_type VARCHAR(20) CHECK (rate_type IN ('daily', 'weekly', 'monthly')),
    change_reason VARCHAR(100),
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pricing_product ON pricing_history(product_id);
CREATE INDEX idx_pricing_dates ON pricing_history(effective_from, effective_to);

-- ============================================
-- CUSTOMER ACTIVITY LOG
-- ============================================

CREATE TABLE customer_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('page_view', 'search', 'add_to_wishlist', 'add_to_cart', 'booking_initiated', 'booking_completed', 'rental_started', 'rental_completed', 'payment_made', 'review_submitted', 'support_ticket')),
    activity_details JSONB DEFAULT '{}',
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    page_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_customer ON customer_activity(customer_id);
CREATE INDEX idx_activity_type ON customer_activity(activity_type);
CREATE INDEX idx_activity_date ON customer_activity(created_at);

-- ============================================
-- REVIEWS
-- ============================================

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rental_id UUID REFERENCES rentals(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    response_text TEXT,
    response_date DATE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_customer ON reviews(customer_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- ============================================
-- ANALYTICS REPORTS
-- ============================================

CREATE TABLE analytics_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(50) NOT NULL,
    report_period VARCHAR(20) CHECK (report_period IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    report_data JSONB NOT NULL,
    generated_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_type ON analytics_reports(report_type);
CREATE INDEX idx_analytics_date ON analytics_reports(start_date);

-- ============================================
-- DEMAND FORECASTS
-- ============================================

CREATE TABLE demand_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    forecast_period VARCHAR(20) CHECK (forecast_period IN ('day', 'week', 'month', 'quarter', 'year')),
    predicted_demand INTEGER NOT NULL,
    confidence_level DECIMAL(5, 2),
    actual_demand INTEGER,
    model_version VARCHAR(20),
    features_used JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecast_product ON demand_forecasts(product_id);
CREATE INDEX idx_forecast_category ON demand_forecasts(category_id);
CREATE INDEX idx_forecast_date ON demand_forecasts(forecast_date);

-- ============================================
-- DYNAMIC PRICING RECOMMENDATIONS
-- ============================================

CREATE TABLE pricing_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    recommendation_date DATE NOT NULL,
    current_rate DECIMAL(10, 2),
    recommended_rate DECIMAL(10, 2),
    min_rate DECIMAL(10, 2),
    max_rate DECIMAL(10, 2),
    demand_factor DECIMAL(5, 2),
    competition_factor DECIMAL(5, 2),
    seasonality_factor DECIMAL(5, 2),
    confidence_score DECIMAL(5, 2),
    recommendation_reason TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users(id),
    applied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pricing_rec_product ON pricing_recommendations(product_id);
CREATE INDEX idx_pricing_rec_date ON pricing_recommendations(recommendation_date);

-- ============================================
-- SYSTEM AUDIT LOG
-- ============================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_date ON audit_log(created_at);

-- ============================================
-- TRIGGER FUNCTIONS
-- ============================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update triggers to all relevant tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I', t, t);
        EXECUTE format('CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Update product availability on rental
CREATE OR REPLACE FUNCTION update_product_availability()
RETURNS TRIGGER AS $$
DECLARE
    new_qty INTEGER;
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status IN ('confirmed', 'in_progress') THEN
        UPDATE products SET available_quantity = available_quantity - 1 WHERE id = NEW.product_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        IF NEW.status IN ('confirmed', 'in_progress') AND OLD.status NOT IN ('confirmed', 'in_progress') THEN
            UPDATE products SET available_quantity = available_quantity - 1 WHERE id = NEW.product_id;
        ELSIF NEW.status = 'completed' AND OLD.status IN ('confirmed', 'in_progress', 'overdue') THEN
            UPDATE products SET available_quantity = available_quantity + 1 WHERE id = NEW.product_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rental_status_change_trigger
AFTER INSERT OR UPDATE OF status ON rentals
FOR EACH ROW EXECUTE FUNCTION update_product_availability();
"""

ANALYTICS_VIEWS = """
-- ============================================
-- ANALYTICS VIEWS
-- ============================================

-- Revenue Summary View
CREATE OR REPLACE VIEW revenue_summary AS
SELECT 
    DATE_TRUNC('day', p.processed_at)::DATE as revenue_date,
    COUNT(DISTINCT p.id) as total_transactions,
    COUNT(DISTINCT r.id) as rental_transactions,
    COALESCE(SUM(CASE WHEN p.payment_type = 'rental' THEN p.amount ELSE 0 END), 0) as rental_revenue,
    COALESCE(SUM(CASE WHEN p.payment_type = 'late_fee' THEN p.amount ELSE 0 END), 0) as late_fee_revenue,
    COALESCE(SUM(CASE WHEN p.payment_type = 'damage_fee' THEN p.amount ELSE 0 END), 0) as damage_fee_revenue,
    COALESCE(SUM(CASE WHEN p.payment_type = 'extension' THEN p.amount ELSE 0 END), 0) as extension_revenue,
    COALESCE(SUM(CASE WHEN p.payment_type = 'refund' THEN -p.amount ELSE 0 END), 0) as refunds,
    COALESCE(SUM(p.amount), 0) as net_revenue
FROM payments p
LEFT JOIN rentals r ON p.rental_id = r.id
WHERE p.payment_status = 'completed'
GROUP BY DATE_TRUNC('day', p.processed_at)::DATE
ORDER BY revenue_date DESC;

-- Product Utilization View
CREATE OR REPLACE VIEW product_utilization AS
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.sku,
    c.name as category_name,
    p.total_quantity,
    p.available_quantity,
    p.daily_rate,
    COUNT(DISTINCT r.id) as total_rentals,
    COALESCE(SUM(r.rental_days), 0) as total_rental_days,
    COALESCE(SUM(r.total_amount), 0) as total_revenue,
    CASE 
        WHEN p.total_quantity > 0 
        THEN ROUND((COUNT(DISTINCT r.id)::DECIMAL / GREATEST(1, p.total_quantity)) * 100, 2)
        ELSE 0 
    END as utilization_rate,
    CASE 
        WHEN p.total_quantity > 0 
        THEN ROUND((SUM(r.rental_days)::DECIMAL / (p.total_quantity * EXTRACT(DAY FROM AGE(CURRENT_DATE, MIN(r.rental_start_date)) + 1))) * 100, 2)
        ELSE 0 
    END as availability_percentage
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN rentals r ON p.id = r.product_id AND r.status IN ('completed', 'in_progress')
WHERE p.is_active = TRUE
GROUP BY p.id, c.name;

-- Customer Analytics View
CREATE OR REPLACE VIEW customer_analytics AS
SELECT 
    c.id as customer_id,
    u.email,
    CONCAT(u.first_name, ' ', u.last_name) as customer_name,
    c.total_rentals,
    c.total_spent,
    COALESCE(c.average_rental_duration, 0) as avg_rental_days,
    c.late_returns_count,
    c.customer_segment,
    c.clv,
    COUNT(DISTINCT r.id) as completed_rentals,
    COUNT(DISTINCT CASE WHEN r.status = 'overdue' THEN r.id END) as overdue_rentals,
    ROUND(
        CASE 
            WHEN COUNT(DISTINCT r.id) > 0 
            THEN (c.late_returns_count::DECIMAL / COUNT(DISTINCT r.id)) * 100 
            ELSE 0 
        END, 2
    ) as late_return_percentage,
    COALESCE(AVG(r.rental_days), 0) as avg_booking_duration
FROM customers c
JOIN users u ON c.user_id = u.id
LEFT JOIN rentals r ON c.id = r.customer_id
WHERE u.is_active = TRUE
GROUP BY c.id, u.email, u.first_name, u.last_name, c.customer_segment, c.clv;

-- Category Performance View
CREATE OR REPLACE VIEW category_performance AS
SELECT 
    cat.id as category_id,
    cat.name as category_name,
    cat.icon,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT r.id) as total_rentals,
    COUNT(DISTINCT c.id) as unique_customers,
    COALESCE(SUM(r.total_amount), 0) as total_revenue,
    COALESCE(AVG(r.total_amount), 0) as avg_rental_value,
    ROUND(AVG(r.rental_days)::DECIMAL, 2) as avg_rental_duration,
    COALESCE(SUM(CASE WHEN r.status = 'overdue' THEN 1 ELSE 0 END), 0) as overdue_count,
    ROUND(
        CASE 
            WHEN COUNT(DISTINCT r.id) > 0 
            THEN (COALESCE(SUM(CASE WHEN r.status = 'overdue' THEN 1 ELSE 0 END), 0)::DECIMAL / COUNT(DISTINCT r.id)) * 100 
            ELSE 0 
        END, 2
    ) as overdue_percentage
FROM categories cat
LEFT JOIN products p ON cat.id = p.category_id AND p.is_active = TRUE
LEFT JOIN rentals r ON p.id = r.product_id
LEFT JOIN customers c ON r.customer_id = c.id
WHERE cat.is_active = TRUE
GROUP BY cat.id;

-- Daily Demand Trend View
CREATE OR REPLACE VIEW daily_demand_trend AS
SELECT 
    DATE(r.rental_start_date) as demand_date,
    c.id as category_id,
    c.name as category_name,
    COUNT(DISTINCT r.id) as rentals_count,
    COUNT(DISTINCT r.product_id) as products_rented,
    COALESCE(SUM(r.total_amount), 0) as daily_revenue
FROM rentals r
JOIN products p ON r.product_id = p.id
JOIN categories c ON p.category_id = c.id
WHERE r.status IN ('confirmed', 'in_progress', 'completed')
GROUP BY DATE(r.rental_start_date), c.id, c.name
ORDER BY demand_date DESC;

-- Inventory Alerts View
CREATE OR REPLACE VIEW inventory_alerts AS
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.sku,
    p.total_quantity,
    p.available_quantity,
    p.daily_rate,
    p.next_maintenance_date,
    CASE 
        WHEN p.available_quantity = 0 THEN 'OUT_OF_STOCK'
        WHEN p.available_quantity < 3 THEN 'LOW_STOCK'
        WHEN p.next_maintenance_date <= CURRENT_DATE THEN 'MAINTENANCE_DUE'
        WHEN p.next_maintenance_date <= CURRENT_DATE + 7 THEN 'MAINTENANCE_SOON'
        ELSE 'OK'
    END as alert_type,
    CASE 
        WHEN p.available_quantity = 0 THEN 3
        WHEN p.available_quantity < 3 THEN 2
        WHEN p.next_maintenance_date <= CURRENT_DATE THEN 3
        ELSE 1
    END as alert_priority
FROM products p
WHERE p.is_active = TRUE
AND (
    p.available_quantity < 3 
    OR p.next_maintenance_date <= CURRENT_DATE + 7
);
"""