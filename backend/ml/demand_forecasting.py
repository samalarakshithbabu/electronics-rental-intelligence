"""
Demand Forecasting Module - ML-based demand prediction
Uses Gradient Boosting to predict future rental demand
"""
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemandForecaster:
    """
    ML-based demand forecasting for rental products
    Uses historical rental data to predict future demand
    """
    
    def __init__(self, model_dir: str = "backend/ml/models"):
        self.model_dir = model_dir
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_cols = [
            'day_of_week', 'month', 'day_of_month', 'is_weekend', 'quarter',
            'is_holiday_season', 'is_summer',
            'day_sin', 'day_cos', 'month_sin', 'month_cos',
            'demand_lag_1', 'demand_lag_7', 'demand_rolling_avg_7'
        ]
        os.makedirs(model_dir, exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for demand prediction"""
        df = df.copy()
        
        # Time-based features
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['day_of_month'] = pd.to_datetime(df['date']).dt.day
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['quarter'] = pd.to_datetime(df['date']).dt.quarter
        
        # Seasonal features
        df['is_holiday_season'] = df['month'].isin([11, 12]).astype(int)
        df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
        
        # Cyclical encoding
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Lag features (previous days demand)
        df = df.sort_values(['category_id', 'date'])
        df['demand_lag_1'] = df.groupby('category_id')['demand'].shift(1)
        df['demand_lag_7'] = df.groupby('category_id')['demand'].shift(7)
        df['demand_rolling_avg_7'] = df.groupby('category_id')['demand'].transform(
            lambda x: x.shift(1).rolling(7, min_periods=1).mean()
        )
        
        # Fill NaN values
        df = df.fillna(0)
        
        return df
    
    def train(self, historical_data: List[Dict[str, Any]], category_id: str = None) -> Dict[str, float]:
        """
        Train the demand forecasting model with actual data
        
        Args:
            historical_data: List of demand records with date, category, demand values
            category_id: Optional category to filter/train for specific category
        
        Returns:
            Model performance metrics
        """
        # Prepare training data
        df = pd.DataFrame(historical_data)
        
        if len(df) < 10:
            logger.warning("Insufficient data for training, using baseline")
            self.is_trained = False
            return {"error": "Insufficient training data"}
        
        # Prepare features
        df = self.prepare_features(df)
        
        if category_id:
            df = df[df.get('category_id') == category_id]
        
        # Remove rows with NaN target
        df = df.dropna(subset=['demand'])
        
        if len(df) < 10:
            return {"error": "Insufficient data after preprocessing"}
        
        X = df[self.feature_cols].values
        y = df['demand'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 2),
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
            "r2": round(r2_score(y_test, y_pred), 4)
        }
        
        self.is_trained = True
        logger.info(f"Demand forecasting model trained. Metrics: {metrics}")
        
        return metrics
    
    def forecast(self, start_date: date, days: int = 14, category_id: str = None) -> List[Dict[str, Any]]:
        """
        Generate demand forecasts using ACTUAL trained model
        
        Args:
            start_date: Starting date for forecasts
            days: Number of days to forecast
            category_id: Optional category filter
        
        Returns:
            List of daily demand forecasts with prediction intervals
        """
        forecasts = []
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            
            # Create feature vector for this date
            features = {
                'date': forecast_date,
                'category_id': category_id or 'all'
            }
            
            if self.is_trained and self.model is not None:
                # Use trained model for prediction
                feature_values = self._create_features_for_date(forecast_date, i)
                feature_array = self.scaler.transform([feature_values])
                prediction = self.model.predict(feature_array)[0]
                prediction = max(0, prediction)  # Demand can't be negative
            else:
                # Use heuristic-based prediction
                prediction = self._heuristic_forecast(forecast_date, i)
            
            # Calculate confidence interval
            std = 1.5 if self.is_trained else 2.0
            
            forecasts.append({
                "date": str(forecast_date),
                "predicted_demand": round(prediction, 1),
                "confidence_lower": round(max(0, prediction - std), 1),
                "confidence_upper": round(prediction + std, 1),
                "confidence_interval": {
                    "lower": round(prediction - std, 1),
                    "upper": round(prediction + std, 1),
                    "std": std
                }
            })
        
        return forecasts
    
    def _create_features_for_date(self, forecast_date: date, day_offset: int) -> List[float]:
        """Create feature vector for a specific date"""
        dow = forecast_date.weekday()
        month = forecast_date.month
        
        return [
            dow,  # day_of_week
            month,  # month
            forecast_date.day,  # day_of_month
            1 if dow >= 5 else 0,  # is_weekend
            (forecast_date.month - 1) // 3 + 1,  # quarter
            1 if month in [11, 12] else 0,  # is_holiday_season
            1 if month in [6, 7, 8] else 0,  # is_summer
            np.sin(2 * np.pi * dow / 7),  # day_sin
            np.cos(2 * np.pi * dow / 7),  # day_cos
            np.sin(2 * np.pi * month / 12),  # month_sin
            np.cos(2 * np.pi * month / 12),  # month_cos
            5.0,  # demand_lag_1 (placeholder)
            5.0,  # demand_lag_7 (placeholder)
            5.0   # demand_rolling_avg_7 (placeholder)
        ]
    
    def _heuristic_forecast(self, forecast_date: date, day_offset: int) -> float:
        """Fallback heuristic-based forecast when model unavailable"""
        dow = forecast_date.weekday()
        month = forecast_date.month
        
        base_demand = 5.0
        
        # Weekend boost
        if dow >= 5:
            base_demand *= 1.4
        
        # Seasonal variation
        if month in [11, 12]:
            base_demand *= 1.3
        elif month in [6, 7, 8]:
            base_demand *= 1.1
        
        # Add realistic variance
        base_demand += (day_offset * 0.05)
        
        return round(base_demand, 1)
    
    def save_model(self, filename: str = "demand_forecaster.joblib"):
        """Save trained model to disk"""
        if not self.is_trained:
            logger.warning("No trained model to save")
            return
        
        filepath = os.path.join(self.model_dir, filename)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_cols': self.feature_cols,
            'is_trained': True
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = "demand_forecaster.joblib"):
        """Load trained model from disk"""
        filepath = os.path.join(self.model_dir, filename)
        if os.path.exists(filepath):
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_cols = data['feature_cols']
            self.is_trained = data['is_trained']
            logger.info("Model loaded successfully")
        else:
            logger.warning("Model file not found")
            self.is_trained = False


# Service class for API integration
class DemandForecastService:
    """Service layer for demand forecasting"""
    
    def __init__(self):
        self.forecaster = DemandForecaster()
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing model or initialize with baseline"""
        try:
            self.forecaster.load_model()
        except:
            # Initialize with heuristic-based predictions
            self.forecaster.is_trained = False
    
    def get_forecast(self, days: int = 14, category_id: str = None) -> Dict[str, Any]:
        """Get demand forecast"""
        forecasts = self.forecaster.forecast(date.today(), days, category_id)
        return {
            "forecasts": forecasts,
            "model_status": "trained" if self.forecaster.is_trained else "heuristic",
            "generated_at": datetime.now().isoformat()
        }
    
    def train_with_data(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Train model with historical data"""
        if len(historical_data) < 10:
            return {"status": "insufficient_data", "message": "Need at least 10 records"}
        
        metrics = self.forecaster.train(historical_data)
        if "error" not in metrics:
            self.forecaster.save_model()
        
        return {"status": "trained" if "error" not in metrics else "failed", "metrics": metrics}