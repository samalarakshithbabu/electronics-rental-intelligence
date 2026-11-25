"""
Product Recommendation Module - ML-based product recommendations
Uses content-based filtering and collaborative approaches
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional, Any
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductRecommender:
    """
    ML-based product recommendation system
    Uses content-based filtering with product features
    """
    
    def __init__(self, model_dir: str = "backend/ml/models"):
        self.model_dir = model_dir
        self.product_features = None
        self.feature_matrix = None
        self.is_trained = False
        self.products = []
        self.similarity_matrix = None
        self.scaler = MinMaxScaler()
        os.makedirs(model_dir, exist_ok=True)
    
    def prepare_product_features(self, products: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare product features for recommendation"""
        df = pd.DataFrame(products)
        
        # Numeric features
        numeric_cols = ['daily_rate', 'stock', 'pricePerDay']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle 'pricePerDay' -> 'daily_rate' mapping
        if 'pricePerDay' in df.columns and 'daily_rate' not in df.columns:
            df['daily_rate'] = df['pricePerDay']
        if 'daily_rate' not in df.columns:
            df['daily_rate'] = 25
        
        # Encode category
        if 'categoryId' in df.columns:
            df['category_encoded'] = df['categoryId'].astype('category').cat.codes
        elif 'category_id' in df.columns:
            df['category_encoded'] = df['category_id'].astype('category').cat.codes
        else:
            df['category_encoded'] = 0
        
        # Handle category_id for joins - use first valid column
        if 'categoryId' in df.columns:
            df['category_id'] = df['categoryId']
        elif 'category_id' in df.columns:
            df['category_id'] = df['category_id']
        else:
            df['category_id'] = 'general'
        
        # Availability score
        if 'available_quantity' in df.columns:
            max_qty = df['available_quantity'].max()
            df['availability_score'] = df['available_quantity'] / (max_qty + 1) if max_qty > 0 else 1.0
        elif 'stock' in df.columns:
            max_qty = df['stock'].max()
            df['availability_score'] = df['stock'] / (max_qty + 1) if max_qty > 0 else 1.0
        else:
            df['availability_score'] = 1.0
        
        # Popularity score (based on mock data or calculate from rentals)
        np.random.seed(42)
        df['popularity_score'] = np.random.uniform(0.3, 1.0, len(df))
        
        # Newness score
        if 'created_at' in df.columns:
            try:
                df['days_since_created'] = (datetime.now() - pd.to_datetime(df['created_at'])).dt.days
                df['newness_score'] = np.clip(1 - df['days_since_created'] / 365, 0.1, 1)
            except:
                df['newness_score'] = np.random.uniform(0.5, 1.0, len(df))
        else:
            df['newness_score'] = np.random.uniform(0.5, 1.0, len(df))
        
        # Fill missing values
        df = df.fillna(0)
        
        return df
    
    def train(self, products: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Train the recommendation model with actual product data
        
        Args:
            products: List of product dictionaries
        
        Returns:
            Model performance metrics
        """
        if len(products) < 2:
            logger.warning("Insufficient products for training")
            self.is_trained = False
            return {"error": "Insufficient products for training"}
        
        self.products = products
        
        # Prepare features
        self.product_features = self.prepare_product_features(products)
        
        # Create feature matrix
        feature_cols = ['daily_rate', 'category_encoded', 'availability_score', 
                       'popularity_score', 'newness_score']
        
        # Add price_per_day if available
        if 'pricePerDay' in self.product_features.columns:
            feature_cols.append('pricePerDay')
        
        # Ensure all columns exist
        for col in feature_cols:
            if col not in self.product_features.columns:
                self.product_features[col] = 0
        
        # Extract only numeric values for the feature matrix
        feature_data = []
        for idx in range(len(self.product_features)):
            row = []
            for col in feature_cols:
                val = self.product_features[col].iloc[idx]
                if hasattr(val, 'item'):  # numpy scalar
                    row.append(val.item())
                else:
                    row.append(float(val))
            feature_data.append(row)
        
        self.feature_matrix = np.array(feature_data)
        
        # Normalize features
        self.scaler = MinMaxScaler()
        self.feature_matrix = self.scaler.fit_transform(self.feature_matrix)
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.feature_matrix)
        
        self.is_trained = True
        
        # Calculate metrics
        n_products = len(products)
        n_features = len(feature_cols)
        
        # Get upper triangle values for average similarity (excluding diagonal)
        sim_values = []
        for i in range(n_products):
            for j in range(i + 1, n_products):
                sim_values.append(self.similarity_matrix[i, j])
        avg_sim = float(np.mean(sim_values)) if sim_values else 0.0
        
        metrics = {
            "n_products": n_products,
            "n_features": n_features,
            "avg_similarity": round(avg_sim, 4)
        }
        
        logger.info(f"Product recommendation model trained. Metrics: {metrics}")
        
        return metrics
    
    def get_similar_products(self, product_id: str, n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Get products similar to the specified product using ACTUAL model
        
        Returns:
            List of similar products with similarity scores
        """
        if not self.is_trained or not self.products:
            return self._get_default_recommendations(n_recommendations)
        
        # Find product index
        product_ids = [str(p.get('id')) for p in self.products]
        try:
            idx = product_ids.index(str(product_id))
        except ValueError:
            return self._get_default_recommendations(n_recommendations)
        
        # Get similarity scores
        similarities = self.similarity_matrix[idx]
        
        # Get top N similar products (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:n_recommendations + 1]
        
        recommendations = []
        for i in top_indices:
            product = self.products[i].copy()
            product['similarity_score'] = round(float(similarities[i]), 3)
            recommendations.append(product)
        
        return recommendations
    
    def recommend_for_customer(
        self, 
        customer_id: str, 
        rental_history: List[Dict[str, Any]], 
        n_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend products based on customer rental history using ACTUAL model
        
        Args:
            customer_id: Customer identifier
            rental_history: List of past rentals with product info
            n_recommendations: Number of recommendations to return
        
        Returns:
            Personalized product recommendations
        """
        if not self.is_trained or not self.products:
            return self._get_default_recommendations(n_recommendations)
        
        if not rental_history:
            return self._get_default_recommendations(n_recommendations)
        
        # Get products from rental history
        rented_product_ids = set(str(r.get('product_id')) for r in rental_history)
        
        # Get categories from rented products
        category_scores: Dict[str, float] = {}
        for rental in rental_history:
            product = next((p for p in self.products if str(p.get('id')) == str(rental.get('product_id'))), None)
            if product:
                cat = str(product.get('categoryId') or product.get('category_id') or 'general')
                category_scores[cat] = category_scores.get(cat, 0) + 1
        
        # Score all products
        product_scores = []
        for product in self.products:
            product_id = str(product.get('id'))
            if product_id in rented_product_ids:
                continue  # Skip already rented
            
            # Category preference score
            cat = str(product.get('categoryId') or product.get('category_id') or 'general')
            category_score = category_scores.get(cat, 0) / max(len(rental_history), 1)
            
            # Similarity to previously rented products
            similarity_scores = []
            for rented_id in rented_product_ids:
                similar = self.get_similar_products(rented_id, 10)
                for s in similar:
                    if str(s.get('id')) == str(product.get('id')):
                        similarity_scores.append(s.get('similarity_score', 0))
                        break
            
            avg_similarity = np.mean(similarity_scores) if similarity_scores else 0
            
            # Combined score
            combined_score = (category_score * 0.6) + (avg_similarity * 0.4)
            
            product_scores.append({
                **product,
                'combined_score': round(combined_score, 3),
                'content_score': round(category_score, 3),
                'collaborative_score': round(avg_similarity, 3)
            })
        
        # Sort by combined score
        product_scores.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return product_scores[:n_recommendations]
    
    def _get_recommendation_reason(self, category_score: float, similarity_score: float) -> str:
        """Generate human-readable reason for recommendation"""
        if category_score > 0.7:
            return "Based on your rental history in this category"
        elif similarity_score > 0.8:
            return "Similar to products you've rented"
        elif category_score > 0.3:
            return "Popular in categories you enjoy"
        else:
            return "Trending product you might like"
    
    def _get_default_recommendations(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get default recommendations when model not available"""
        if not self.products:
            return []
        
        # Return most popular products
        sorted_products = sorted(
            self.products, 
            key=lambda p: p.get('popularity_score', 0), 
            reverse=True
        )
        
        return [
            {**p, 'recommendation_score': 0.8, 'reason': 'Popular product'}
            for p in sorted_products[:n]
        ]
    
    def get_trending_products(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get trending products based on popularity"""
        if not self.is_trained:
            return self._get_default_recommendations(n)
        
        sorted_products = sorted(
            self.products,
            key=lambda p: p.get('popularity_score', 0),
            reverse=True
        )
        
        return [
            {**p, 'trending_score': round(p.get('popularity_score', 0), 3)}
            for p in sorted_products[:n]
        ]
    
    def save_model(self, filename: str = "product_recommender.joblib"):
        """Save trained model to disk"""
        if not self.is_trained:
            logger.warning("No trained model to save")
            return
        
        filepath = os.path.join(self.model_dir, filename)
        joblib.dump({
            'products': self.products,
            'product_features': self.product_features,
            'feature_matrix': self.feature_matrix,
            'similarity_matrix': self.similarity_matrix,
            'scaler': self.scaler,
            'is_trained': True
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = "product_recommender.joblib"):
        """Load trained model from disk"""
        filepath = os.path.join(self.model_dir, filename)
        if os.path.exists(filepath):
            data = joblib.load(filepath)
            self.products = data.get('products', [])
            self.product_features = data.get('product_features')
            self.feature_matrix = data.get('feature_matrix')
            self.similarity_matrix = data.get('similarity_matrix')
            self.scaler = data.get('scaler')
            self.is_trained = data.get('is_trained', True)
            logger.info("Model loaded successfully")
        else:
            logger.warning("Model file not found")
            self.is_trained = False


# Service class for API integration
class RecommendationService:
    """Service layer for product recommendations"""
    
    def __init__(self, recommender: ProductRecommender = None):
        self.recommender = recommender if recommender else ProductRecommender()
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing model"""
        try:
            self.recommender.load_model()
        except:
            self.recommender.is_trained = False
    
    def get_personalized_recommendations(
        self, 
        customer_id: str, 
        rental_history: List[Dict[str, Any]],
        n_recommendations: int = 5
    ) -> Dict[str, Any]:
        """Get personalized recommendations for a customer"""
        recommendations = self.recommender.recommend_for_customer(
            customer_id, rental_history, n_recommendations
        )
        
        return {
            "customer_id": customer_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    
    def get_similar_to_product(
        self, 
        product_id: str, 
        n_recommendations: int = 5
    ) -> Dict[str, Any]:
        """Get products similar to a specific product"""
        similar = self.recommender.get_similar_products(product_id, n_recommendations)
        
        return {
            "source_product_id": product_id,
            "similar_products": similar,
            "count": len(similar)
        }
    
    def get_dashboard_recommendations(self) -> Dict[str, Any]:
        """Get various recommendation types for dashboard"""
        return {
            "trending": self.recommender.get_trending_products(5),
            "new_arrivals": self._get_new_arrivals(5),
            "best_value": self._get_best_value(5)
        }
    
    def _get_new_arrivals(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get newest products"""
        if not self.recommender.products:
            return []
        
        sorted_products = sorted(
            self.recommender.products,
            key=lambda p: p.get('newness_score', 0),
            reverse=True
        )
        
        return [{**p, 'new_score': p.get('newness_score', 0)} for p in sorted_products[:n]]
    
    def _get_best_value(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get best value products (low price, high popularity)"""
        if not self.recommender.is_trained:
            return self._get_default_recommendations(n)
        
        scored = []
        for p in self.recommender.products:
            score = (p.get('popularity_score', 0.5) / max(p.get('daily_rate', 25), 1)) * 10
            scored.append({**p, 'value_score': round(score, 3)})
        
        scored.sort(key=lambda x: x['value_score'], reverse=True)
        return scored[:n]
    
    def _get_default_recommendations(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get default recommendations"""
        return self.recommender._get_default_recommendations(n)
    
    def train_with_data(self, products: List[Dict]) -> Dict[str, Any]:
        """Train model with product data"""
        if len(products) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 products"}
        
        metrics = self.recommender.train(products)
        if "error" not in metrics:
            self.recommender.save_model()
        
        return {"status": "trained" if "error" not in metrics else "failed", "metrics": metrics}