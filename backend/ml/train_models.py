"""
ML Training Script - Train all ML models with synthetic data
Run this script to train models and save them for production use
"""
import sys
import os
import json
import numpy as np
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.demand_forecasting import DemandForecaster
from ml.customer_segmentation import CustomerSegmenter
from ml.recommendations import ProductRecommender
from ml.orchestrator import MLOrchestrator

# Set random seed for reproducibility
np.random.seed(42)

def generate_synthetic_demand_data(n_records: int = 365) -> list:
    """Generate synthetic demand historical data"""
    data = []
    start_date = date.today() - timedelta(days=n_records)
    
    for i in range(n_records):
        current_date = start_date + timedelta(days=i)
        month = current_date.month
        dow = current_date.weekday()
        
        # Base demand with seasonal patterns
        base_demand = 5.0
        
        # Weekend boost
        if dow >= 5:
            base_demand *= 1.4
        
        # Seasonal variation
        if month in [11, 12]:  # Holiday season
            base_demand *= 1.3
        elif month in [6, 7, 8]:  # Summer
            base_demand *= 1.1
        
        # Add random variation
        demand = base_demand + np.random.normal(0, 1.5)
        demand = max(0, round(demand, 1))
        
        data.append({
            "date": str(current_date),
            "category_id": f"category-{np.random.randint(1, 7)}",
            "demand": demand
        })
    
    return data


def generate_synthetic_customers(n_customers: int = 100) -> list:
    """Generate synthetic customer data"""
    customers = []
    
    for i in range(n_customers):
        # Random distribution of customer types
        rand = np.random.random()
        if rand < 0.3:  # 30% new customers
            rentals = np.random.randint(1, 3)
            spent = np.random.randint(50, 200)
        elif rand < 0.6:  # 30% regular
            rentals = np.random.randint(3, 8)
            spent = np.random.randint(200, 600)
        elif rand < 0.85:  # 25% premium
            rentals = np.random.randint(8, 15)
            spent = np.random.randint(600, 1500)
        else:  # 15% VIP
            rentals = np.random.randint(15, 30)
            spent = np.random.randint(1500, 5000)
        
        customers.append({
            "id": f"customer-{i:04d}",
            "email": f"customer{i}@example.com",
            "name": f"Customer {i}",
            "total_rentals": rentals,
            "total_spent": spent,
            "average_rental_duration": round(np.random.uniform(3, 10), 1),
            "late_returns_pct": round(np.random.uniform(0, 15), 1),
            "engagement_score": round(np.random.uniform(40, 100), 1),
            "is_active": True
        })
    
    return customers


def generate_synthetic_products(n_products: int = 30) -> list:
    """Generate synthetic product data"""
    categories = ["laptops", "cameras", "audio", "gaming", "smart-home", "tablets"]
    category_names = {
        "laptops": "Laptops",
        "cameras": "Cameras", 
        "audio": "Audio Equipment",
        "gaming": "Gaming",
        "smart-home": "Smart Home",
        "tablets": "Tablets"
    }
    base_prices = {
        "laptops": 45,
        "cameras": 40,
        "audio": 15,
        "gaming": 25,
        "smart-home": 12,
        "tablets": 30
    }
    
    products = []
    
    for i in range(n_products):
        category = categories[i % len(categories)]
        base_price = base_prices[category]
        
        products.append({
            "id": f"prod-{i:04d}",
            "sku": f"SKU-{category[:3].upper()}-{i:04d}",
            "name": f"{category_names[category]} Product {i}",
            "categoryId": category,
            "daily_rate": base_price + np.random.randint(-10, 15),
            "pricePerDay": base_price + np.random.randint(-10, 15),
            "stock": np.random.randint(1, 10),
            "available_quantity": np.random.randint(0, 8),
            "is_active": True,
            "created_at": (date.today() - timedelta(days=np.random.randint(30, 365))).isoformat()
        })
    
    return products


def generate_synthetic_rentals(
    products: list, 
    customers: list, 
    n_rentals: int = 500
) -> list:
    """Generate synthetic rental history"""
    rentals = []
    product_ids = [p["id"] for p in products]
    customer_ids = [c["id"] for c in customers]
    
    for i in range(n_rentals):
        product_id = np.random.choice(product_ids)
        customer_id = np.random.choice(customer_ids)
        
        days_ago = np.random.randint(1, 180)
        start_date = date.today() - timedelta(days=days_ago)
        duration = np.random.randint(1, 14)
        end_date = start_date + timedelta(days=duration)
        
        # Find product price
        product = next((p for p in products if p["id"] == product_id), None)
        daily_rate = product["daily_rate"] if product else 25
        
        status = "completed" if end_date < date.today() else "in_progress"
        
        rentals.append({
            "id": f"rental-{i:05d}",
            "rental_number": f"RN-{i:06d}",
            "product_id": product_id,
            "customer_id": customer_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "rental_days": duration,
            "daily_rate": daily_rate,
            "total_amount": daily_rate * duration,
            "status": status
        })
    
    return rentals


def main():
    """Main training function"""
    print("=" * 60)
    print("AI-Powered Electronics Rental and Revenue Intelligence - ML Model Training")
    print("=" * 60)
    print()
    
    # Generate synthetic data
    print("[1/5] Generating synthetic data...")
    
    products = generate_synthetic_products(30)
    customers = generate_synthetic_customers(100)
    rentals = generate_synthetic_rentals(products, customers, 500)
    demand_data = generate_synthetic_demand_data(365)
    
    print(f"  - Products: {len(products)}")
    print(f"  - Customers: {len(customers)}")
    print(f"  - Rentals: {len(rentals)}")
    print(f"  - Demand records: {len(demand_data)}")
    print()
    
    # Train demand forecasting model
    print("[2/5] Training Demand Forecasting Model...")
    demand_forecaster = DemandForecaster()
    demand_metrics = demand_forecaster.train(demand_data)
    print(f"  - Metrics: {demand_metrics}")
    demand_forecaster.save_model()
    print("  - Saved to: backend/ml/models/demand_forecaster.joblib")
    print()
    
    # Train customer segmentation model
    print("[3/5] Training Customer Segmentation Model...")
    customer_segmenter = CustomerSegmenter()
    customer_metrics = customer_segmenter.train(customers)
    print(f"  - Metrics: {customer_metrics}")
    customer_segmenter.save_model()
    print("  - Saved to: backend/ml/models/customer_segmenter.joblib")
    print()
    
    # Train product recommendation model
    print("[4/5] Training Product Recommendation Model...")
    product_recommender = ProductRecommender()
    product_metrics = product_recommender.train(products)
    print(f"  - Metrics: {product_metrics}")
    product_recommender.save_model()
    print("  - Saved to: backend/ml/models/product_recommender.joblib")
    print()
    
    # Initialize orchestrator
    print("[5/5] Initializing ML Orchestrator...")
    orchestrator = MLOrchestrator()
    init_results = orchestrator.initialize(products, customers, demand_data)
    print(f"  - Results: {init_results}")
    print()
    
    # Generate sample predictions
    print("=" * 60)
    print("Sample Predictions:")
    print("=" * 60)
    print()
    
    # Demand forecast
    forecasts = orchestrator.get_demand_forecast(7)
    print("Demand Forecast (next 7 days):")
    for f in forecasts["forecasts"][:3]:
        print(f"  - {f['date']}: {f['predicted_demand']} rentals")
    print()
    
    # Customer segments
    print("Customer Segment Distribution:")
    segments = orchestrator.get_customer_segments(customers[:10])
    print(f"  - Predictions: {len(segments['predictions'])} customers")
    print()
    
    # Product recommendations
    print("Product Recommendations for customer-0001:")
    recs = orchestrator.get_product_recommendations(
        "customer-0001",
        [{"product_id": "prod-0000"}],
        3
    )
    for rec in recs["recommendations"]:
        print(f"  - {rec['name']}: {rec['reason']}")
    print()
    
    # Save training summary
    summary = {
        "training_date": str(date.today()),
        "models": {
            "demand_forecasting": {
                "status": "trained",
                "metrics": demand_metrics,
                "model_file": "backend/ml/models/demand_forecaster.joblib"
            },
            "customer_segmentation": {
                "status": "trained",
                "metrics": customer_metrics,
                "model_file": "backend/ml/models/customer_segmenter.joblib"
            },
            "product_recommendations": {
                "status": "trained",
                "metrics": product_metrics,
                "model_file": "backend/ml/models/product_recommender.joblib"
            }
        },
        "data_summary": {
            "n_products": len(products),
            "n_customers": len(customers),
            "n_rentals": len(rentals),
            "demand_records": len(demand_data)
        }
    }
    
    summary_file = "backend/ml/training_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("=" * 60)
    print("Training Complete!")
    print(f"Summary saved to: {summary_file}")
    print("=" * 60)
    
    return summary


if __name__ == "__main__":
    main()