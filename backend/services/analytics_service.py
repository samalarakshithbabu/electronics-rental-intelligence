"""
Analytics Service - Core business metrics and reporting
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from sqlalchemy.sql import label
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get revenue summary for a date range"""
        from backend.models import Payment, Rental
        
        # Total revenue
        total_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.payment_status == 'completed',
            Payment.payment_type == 'rental',
            Payment.processed_at >= start_date,
            Payment.processed_at <= end_date + timedelta(days=1)
        ).scalar() or 0
        
        # Monthly revenue breakdown
        monthly_revenue = self.db.query(
            func.date_trunc('month', Payment.processed_at).label('month'),
            func.sum(Payment.amount).label('revenue')
        ).filter(
            Payment.payment_status == 'completed',
            Payment.payment_type == 'rental',
            Payment.processed_at >= start_date,
            Payment.processed_at <= end_date + timedelta(days=1)
        ).group_by('month').order_by(desc('month')).all()
        
        # Revenue by category
        from backend.models import Category, Product, Rental
        category_revenue = self.db.query(
            Category.name,
            func.sum(Rental.total_amount).label('revenue'),
            func.count(Rental.id).label('rentals')
        ).join(Product, Category.id == Product.category_id).join(
            Rental, Product.id == Rental.product_id
        ).filter(
            Rental.status.in_(['completed', 'in_progress']),
            Rental.created_at >= start_date,
            Rental.created_at <= end_date + timedelta(days=1)
        ).group_by(Category.name).all()
        
        return {
            "total_revenue": float(total_revenue),
            "monthly_breakdown": [
                {"month": str(m.month), "revenue": float(m.revenue)} 
                for m in monthly_revenue
            ],
            "category_revenue": [
                {"category": c[0], "revenue": float(c[1]), "rentals": c[2]}
                for c in category_revenue
            ]
        }
    
    def get_product_utilization(self) -> List[Dict[str, Any]]:
        """Calculate product utilization rates"""
        from backend.models import Product, Rental
        
        products = self.db.query(Product).filter(Product.is_active == True).all()
        utilization_data = []
        
        for product in products:
            # Get all completed rentals for this product
            rentals = self.db.query(Rental).filter(
                Rental.product_id == product.id,
                Rental.status == 'completed'
            ).all()
            
            total_rentals = len(rentals)
            total_rental_days = sum(r.rental_days for r in rentals)
            total_revenue = sum(r.total_amount for r in rentals)
            
            # Calculate utilization (rental days / total available days)
            product_age_days = max(1, (date.today() - min(r.rental_start_date for r in rentals) if rentals else date.today() - product.created_at.date()).days)
            utilization_rate = (total_rental_days / (product.total_quantity * product_age_days * 24)) * 100 if product_age_days > 0 else 0
            
            utilization_data.append({
                "product_id": str(product.id),
                "name": product.name,
                "sku": product.sku,
                "total_rentals": total_rentals,
                "total_rental_days": total_rental_days,
                "total_revenue": float(total_revenue),
                "available_quantity": product.available_quantity,
                "daily_rate": product.daily_rate,
                "utilization_rate": round(utilization_rate, 2)
            })
        
        # Sort by utilization rate descending
        utilization_data.sort(key=lambda x: x['utilization_rate'], reverse=True)
        return utilization_data
    
    def get_customer_analytics(self) -> Dict[str, Any]:
        """Calculate customer-related metrics"""
        from backend.models import Customer, Rental
        from backend.models import User
        
        # Customer distribution by segment
        segment_dist = self.db.query(
            Customer.customer_segment,
            func.count(Customer.id)
        ).group_by(Customer.customer_segment).all()
        
        # Customer retention
        total_customers = self.db.query(func.count(Customer.id)).scalar() or 0
        repeat_customers = self.db.query(func.count(func.distinct(Customer.id))).filter(
            Customer.total_rentals > 1
        ).scalar() or 0
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Customer lifetime value
        avg_clv = self.db.query(func.avg(Customer.clv)).scalar() or 0
        
        # Average rental duration
        avg_duration = self.db.query(func.avg(Rental.rental_days)).filter(
            Rental.status == 'completed'
        ).scalar() or 0
        
        # Late return rate
        late_returns = self.db.query(func.count(Rental.id)).filter(
            Rental.status == 'completed',
            Rental.actual_return_date > Rental.rental_end_date
        ).scalar() or 0
        completed_rentals = self.db.query(func.count(Rental.id)).filter(
            Rental.status == 'completed'
        ).scalar() or 0
        late_rate = (late_returns / completed_rentals * 100) if completed_rentals > 0 else 0
        
        return {
            "segment_distribution": {
                seg[0]: seg[1] for seg in segment_dist if seg[0]
            },
            "total_customers": total_customers,
            "repeat_customers": repeat_customers,
            "retention_rate": round(retention_rate, 2),
            "average_clv": round(float(avg_clv), 2),
            "average_rental_duration": round(float(avg_duration), 2),
            "late_return_percentage": round(late_rate, 2)
        }
    
    def get_demand_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze demand trends"""
        from backend.models import Rental, Product, Category
        from datetime import datetime, timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Daily rental counts
        daily_demand = self.db.query(
            func.date(Rental.rental_start_date).label('date'),
            func.count(Rental.id).label('rentals')
        ).filter(
            Rental.rental_start_date >= start_date,
            Rental.rental_start_date <= end_date,
            Rental.status.in_(['confirmed', 'in_progress', 'completed'])
        ).group_by('date').order_by(desc('date')).all()
        
        # Top categories by demand
        top_categories = self.db.query(
            Category.name,
            func.count(Rental.id).label('rentals'),
            func.sum(Rental.total_amount).label('revenue')
        ).join(Product, Category.id == Product.category_id).join(
            Rental, Product.id == Rental.product_id
        ).filter(
            Rental.rental_start_date >= start_date
        ).group_by(Category.name).order_by(desc('rentals')).limit(5).all()
        
        return {
            "daily_demand": [
                {"date": str(d[0]), "rentals": d[1]} for d in daily_demand
            ],
            "top_categories": [
                {"category": c[0], "rentals": c[1], "revenue": float(c[2])}
                for c in top_categories
            ]
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get key metrics for admin dashboard"""
        from backend.models import Product, Customer, Rental, Payment
        
        # Basic counts
        total_products = self.db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0
        available_products = self.db.query(func.sum(Product.available_quantity)).filter(Product.is_active == True).scalar() or 0
        total_customers = self.db.query(func.count(Customer.id)).scalar() or 0
        active_rentals = self.db.query(func.count(Rental.id)).filter(
            Rental.status == 'in_progress'
        ).scalar() or 0
        overdue_rentals = self.db.query(func.count(Rental.id)).filter(
            Rental.status == 'overdue'
        ).scalar() or 0
        
        # Revenue metrics
        today_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.payment_status == 'completed',
            Payment.payment_type == 'rental',
            func.date(Payment.processed_at) == date.today()
        ).scalar() or 0
        
        month_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.payment_status == 'completed',
            Payment.payment_type == 'rental',
            func.date_trunc('month', Payment.processed_at) == func.date_trunc('month', func.current_date())
        ).scalar() or 0
        
        # Calculate growth
        last_month_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.payment_status == 'completed',
            Payment.payment_type == 'rental',
            func.date_trunc('month', Payment.processed_at) == func.date_trunc('month', func.current_date() - func.interval('1 month'))
        ).scalar() or 0
        revenue_growth = ((month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
        
        # Product utilization
        avg_utilization = self.db.query(
            func.avg(
                case(
                    (Product.total_quantity > 0,
                     (Product.total_quantity - Product.available_quantity).cast(Float) / Product.total_quantity * 100),
                    else_=0
                )
            )
        ).filter(Product.is_active == True).scalar() or 0
        
        return {
            "total_revenue_today": float(today_revenue),
            "total_revenue_month": float(month_revenue),
            "revenue_growth": round(float(revenue_growth), 2),
            "total_products": total_products,
            "available_items": int(available_products),
            "total_customers": total_customers,
            "active_rentals": active_rentals,
            "overdue_rentals": overdue_rentals,
            "average_utilization": round(float(avg_utilization), 2)
        }


def get_analytics_service(db: Session) -> AnalyticsService:
    return AnalyticsService(db)