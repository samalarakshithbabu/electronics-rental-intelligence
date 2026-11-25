"""
Customer Segmentation Module - ML-based customer clustering
Uses K-Means clustering to segment customers based on behavior
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerSegmenter:
    """
    ML-based customer segmentation using K-Means clustering
    Segments customers into: new, regular, premium, VIP
    """
    
    def __init__(self, model_dir: str = "backend/ml/models"):
        self.model_dir = model_dir
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_cols = [
            'total_rentals', 'total_spent', 'avg_rental_duration',
            'late_returns_pct', 'retention_score', 'engagement_score'
        ]
        self.cluster_to_segment = {}
        os.makedirs(model_dir, exist_ok=True)
    
    def prepare_features(self, customers: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare customer features for clustering"""
        df = pd.DataFrame(customers)
        
        # Calculate derived features
        if 'total_rentals' not in df.columns:
            df['total_rentals'] = 0
        if 'total_spent' not in df.columns:
            df['total_spent'] = 0
        
        df['avg_rental_duration'] = df.apply(
            lambda x: x['total_rentals'] * 5 if x['total_rentals'] > 0 else np.random.uniform(3, 10),
            axis=1
        )
        df['late_returns_pct'] = np.random.uniform(0, 15, len(df)) if 'late_returns_pct' not in df.columns else df['late_returns_pct']
        
        max_rentals = df['total_rentals'].max() if df['total_rentals'].max() > 0 else 1
        df['retention_score'] = (df['total_rentals'] / max_rentals) * 100
        
        df['engagement_score'] = np.random.uniform(30, 100, len(df)) if 'engagement_score' not in df.columns else df['engagement_score']
        
        # Fill missing values
        df = df.fillna(0)
        
        return df
    
    def train(self, customers: List[Dict[str, Any]], n_clusters: int = 4) -> Dict[str, float]:
        """
        Train the customer segmentation model with actual customer data
        
        Args:
            customers: List of customer data dictionaries
            n_clusters: Number of clusters (default: 4 for new/regular/premium/VIP)
        
        Returns:
            Model performance metrics
        """
        # Prepare features
        df = self.prepare_features(customers)
        
        if len(df) < n_clusters:
            logger.warning("Insufficient customers for clustering")
            self.is_trained = False
            return {"error": "Insufficient data for training"}
        
        # Extract features
        X = df[self.feature_cols].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train K-Means
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        self.model.fit(X_scaled)
        
        # Add cluster labels to dataframe
        df['cluster'] = self.model.labels_
        
        # Calculate metrics
        silhouette = silhouette_score(X_scaled, self.model.labels_)
        
        # Map clusters to segments based on characteristics
        cluster_stats = df.groupby('cluster').agg({
            'total_rentals': 'mean',
            'total_spent': 'mean'
        }).to_dict('index')
        
        # Create segment mapping based on spending/rentals
        segment_mapping = {}
        clusters_by_value = sorted(
            cluster_stats.items(),
            key=lambda x: (x[1]['total_rentals'] + x[1]['total_spent'] / 100),
            reverse=True
        )
        
        segments = ['vip', 'premium', 'regular', 'new']
        for idx, (cluster_id, _) in enumerate(clusters_by_value):
            if idx < len(segments):
                segment_mapping[cluster_id] = segments[idx]
            else:
                segment_mapping[cluster_id] = 'new'
        
        self.cluster_to_segment = segment_mapping
        df['segment'] = df['cluster'].map(segment_mapping)
        
        self.is_trained = True
        
        metrics = {
            "silhouette_score": round(silhouette, 4),
            "n_customers": len(customers),
            "n_clusters": n_clusters,
            "segment_distribution": df['segment'].value_counts().to_dict()
        }
        
        logger.info(f"Customer segmentation model trained. Metrics: {metrics}")
        
        return metrics
    
    def predict_segment(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict segment for a single customer
        
        Args:
            customer_data: Customer data dictionary
        
        Returns:
            Segment prediction with details
        """
        if not self.is_trained:
            # Return default segment
            return {
                "segment": "new",
                "description": "New customer - no rental history",
                "benefits": ["Welcome discount", "Flexible rental terms"],
                "recommended_actions": ["Encourage first rental", "Welcome email"]
            }
        
        # Prepare features
        df = pd.DataFrame([customer_data])
        df = self.prepare_features(df)
        
        # Extract and scale features
        X = df[self.feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        # Predict cluster
        cluster = self.model.predict(X_scaled)[0]
        segment = self.cluster_to_segment.get(cluster, 'new')
        
        # Get segment details
        segment_details = self._get_segment_details(segment)
        
        return segment_details
    
    def _get_segment_details(self, segment: str) -> Dict[str, Any]:
        """Get details for a customer segment"""
        segment_info = {
            'new': {
                'description': 'New customer with 1-2 rentals',
                'benefits': ['Welcome discount (10%)', 'Priority support', 'Flexible rental terms'],
                'recommended_actions': ['Send welcome email', 'Offer first-time promotion', 'Request review after first rental']
            },
            'regular': {
                'description': 'Active customer with 3-7 rentals',
                'benefits': ['15% discount on rentals', 'Free extensions', 'Loyalty points', 'Birthday bonus'],
                'recommended_actions': ['Cross-sell related products', 'Offer subscription plan', 'Feature new arrivals']
            },
            'premium': {
                'description': 'Valuable customer with 8-14 rentals',
                'benefits': ['20% discount', 'Free express shipping', 'Extended rental periods', 'VIP support line', 'Exclusive access to new products'],
                'recommended_actions': ['Personal account manager', 'Invite to beta testing', 'Partner offers']
            },
            'vip': {
                'description': 'Top customer with 15+ rentals',
                'benefits': ['25% discount', 'Free premium accessories', 'Concierge service', 'Annual gift', 'Early access to all products', 'Complimentary insurance'],
                'recommended_actions': ['Annual loyalty review', 'Premium partnership offers', 'Exclusive events invitation', 'Custom product requests']
            }
        }
        
        return {
            'segment': segment,
            'description': segment_info.get(segment, {}).get('description', 'Customer'),
            'benefits': segment_info.get(segment, {}).get('benefits', []),
            'recommended_actions': segment_info.get(segment, {}).get('recommended_actions', [])
        }
    
    def get_all_segments(self, customers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get segment predictions for multiple customers"""
        if not self.is_trained or not customers:
            return {
                "predictions": [
                    self._get_segment_details('new')
                    for _ in range(min(10, len(customers)))
                ],
                "segment_counts": {
                    "new": len(customers),
                    "regular": 0,
                    "premium": 0,
                    "vip": 0
                }
            }
        
        predictions = []
        for customer in customers:
            pred = self.predict_segment(customer)
            predictions.append({
                "customer_id": customer.get('id', 'unknown'),
                **pred
            })
        
        # Count segments
        segment_counts = {
            "new": 0,
            "regular": 0,
            "premium": 0,
            "vip": 0
        }
        for pred in predictions:
            segment_counts[pred['segment']] = segment_counts.get(pred['segment'], 0) + 1
        
        return {
            "predictions": predictions,
            "segment_counts": segment_counts
        }
    
    def save_model(self, filename: str = "customer_segmenter.joblib"):
        """Save trained model to disk"""
        if not self.is_trained:
            logger.warning("No trained model to save")
            return
        
        filepath = os.path.join(self.model_dir, filename)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_cols': self.feature_cols,
            'cluster_to_segment': self.cluster_to_segment,
            'is_trained': True
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = "customer_segmenter.joblib"):
        """Load trained model from disk"""
        filepath = os.path.join(self.model_dir, filename)
        if os.path.exists(filepath):
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_cols = data['feature_cols']
            self.cluster_to_segment = data['cluster_to_segment']
            self.is_trained = data['is_trained']
            logger.info("Model loaded successfully")
        else:
            logger.warning("Model file not found")
            self.is_trained = False


# Service class for API integration
class CustomerSegmentationService:
    """Service layer for customer segmentation"""
    
    def __init__(self):
        self.segmenter = CustomerSegmenter()
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing model or initialize"""
        try:
            self.segmenter.load_model()
        except:
            self.segmenter.is_trained = False
    
    def get_segment(self, customer_data: Dict) -> Dict[str, Any]:
        """Get segment for a customer"""
        return self.segmenter.predict_segment(customer_data)
    
    def get_all_segments(self, customers: List[Dict]) -> Dict[str, Any]:
        """Get segments for all customers"""
        return self.segmenter.get_all_segments(customers)
    
    def train_with_data(self, customers: List[Dict]) -> Dict[str, Any]:
        """Train model with customer data"""
        if len(customers) < 4:
            return {"status": "insufficient_data", "message": "Need at least 4 customers"}
        
        metrics = self.segmenter.train(customers)
        if "error" not in metrics:
            self.segmenter.save_model()
        
        return {"status": "trained" if "error" not in metrics else "failed", "metrics": metrics}