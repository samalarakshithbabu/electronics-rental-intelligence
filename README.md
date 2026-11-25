# ElectroRent AI - Smart Rental & Revenue Intelligence Platform

A production-quality, AI-powered electronic gadget rental platform with advanced analytics, machine learning, and business intelligence features.

![ElectroRent AI Dashboard](https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200)

## 🚀 Features

### Core Rental Management
- **Smart Inventory Management** - Track electronic gadgets with detailed specifications
- **Customer Registration & Profiles** - Comprehensive customer management
- **Rental Booking & Returns** - Complete rental lifecycle management
- **Availability Tracking** - Real-time inventory status
- **Payment Processing** - Integrated payment handling

### AI-Powered Analytics
- **Demand Forecasting** - ML-based prediction of future rental demand using Gradient Boosting
- **Dynamic Pricing** - AI-optimized pricing recommendations based on demand, seasonality, and competition
- **Revenue Intelligence** - Comprehensive revenue analytics and insights
- **Customer Segmentation** - Automatic customer clustering (New, Regular, Premium, VIP)
- **Utilization Analytics** - Product performance and utilization tracking

### Business Intelligence Dashboard
- **Real-time Metrics** - Revenue, rentals, active users, and inventory KPIs
- **Interactive Charts** - Revenue trends, category distribution, demand forecasts
- **Actionable Insights** - AI-generated business recommendations
- **Product Performance** - Utilization rates and revenue by product

### Premium UI/UX
- **Modern Dashboard** - Premium SaaS-style admin interface
- **Dark/Light Modes** - Full theme support
- **Responsive Design** - Mobile-first responsive layouts
- **Smooth Animations** - Framer Motion animations
- **Interactive Visualizations** - Recharts data visualization

## 🛠 Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Full type safety
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Recharts** - Interactive charts
- **React Router** - Client-side routing
- **Vite** - Fast build tool

### Backend
- **Python 3.11+** - Core runtime
- **FastAPI** - High-performance API framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Production database
- **Pydantic** - Data validation

### Data Science & ML
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - ML algorithms (Gradient Boosting, Random Forest)
- **Matplotlib/Seaborn** - Static visualizations

## 📁 Project Structure

```
ElectroRent-master/
├── src/
│   ├── pages/
│   │   ├── Admin/
│   │   │   └── AdminDashboard.tsx    # AI-powered admin dashboard
│   │   ├── HomePage.tsx
│   │   ├── CategoryPage.tsx
│   │   ├── ProductPage.tsx
│   │   ├── CartPage.tsx
│   │   └── ...
│   ├── components/
│   │   ├── NavBar.tsx
│   │   ├── ProductCard.tsx
│   │   ├── SearchBar.tsx
│   │   └── ...
│   ├── context/
│   │   ├── AuthContext.tsx
│   │   ├── CartContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── ...
│   ├── data/
│   │   └── mockData.ts               # Product catalog
│   ├── types/
│   │   └── index.ts                  # TypeScript definitions
│   └── services/
│       └── apiService.ts             # API integrations
├── backend/
│   ├── main.py                       # FastAPI application
│   ├── models/                       # SQLAlchemy models
│   │   └── __init__.py
│   ├── services/                     # Business logic
│   │   └── analytics_service.py
│   ├── ml/                           # Machine learning
│   │   ├── demand_forecasting.py
│   │   └── dynamic_pricing.py
│   ├── database/
│   │   └── schema.py                 # PostgreSQL schema
│   └── requirements.txt
└── package.json
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+ (optional, uses in-memory for demo)

### Frontend Setup

```bash
# Navigate to project
cd ElectroRent-master

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
python backend/main.py
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 API Endpoints

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/analytics/revenue` - Revenue analytics
- `GET /api/analytics/products` - Product performance
- `GET /api/analytics/customers` - Customer analytics

### Demand Forecasting
- `GET /api/forecasting/demand` - 14-day demand forecast
- `GET /api/forecasting/category/{id}` - Category-specific forecast

### Dynamic Pricing
- `GET /api/pricing/recommendations` - All pricing recommendations
- `GET /api/pricing/product/{id}` - Product pricing details

### Business Intelligence
- `GET /api/business/insights` - AI-generated insights
- `GET /api/business/opportunities` - Revenue opportunities

### Rentals
- `POST /api/rentals` - Create rental
- `GET /api/rentals` - List rentals
- `POST /api/rentals/{id}/return` - Process return

## 🧮 Machine Learning Features

### Demand Forecasting Model
- **Algorithm**: Gradient Boosting Regressor
- **Features**: Day of week, month, seasonality, lag features
- **Output**: 14-day demand predictions with confidence intervals
- **Accuracy**: MAE, RMSE, R² metrics

### Dynamic Pricing Engine
- **Factors Considered**:
  - Demand factor (current vs historical)
  - Availability factor (scarcity pricing)
  - Seasonality factor
  - Day of week factor
  - Competition factor
  - Depreciation factor

### Customer Analytics
- **Segmentation**: K-means clustering
- **CLV Calculation**: Customer lifetime value
- **Retention Metrics**: Churn prediction

## 📈 Key Metrics Tracked

| Metric | Description |
|--------|-------------|
| Total Revenue | Cumulative revenue |
| Active Rentals | Currently rented items |
| Overdue Returns | Late returns count |
| Product Utilization | Rental days / Available days |
| Customer Retention | Repeat customer rate |
| Revenue Growth | Month-over-month growth |
| Demand Forecast | Predicted future demand |
| Price Optimization | Recommended price changes |

## 🎨 UI Components

### Admin Dashboard
- **KPI Cards**: Key metrics with trends
- **Revenue Chart**: Area chart with dual Y-axis
- **Demand Forecast**: Time-series prediction chart
- **Category Distribution**: Pie chart
- **Pricing Recommendations**: Before/after comparisons
- **Business Insights**: Actionable recommendations
- **Product Table**: Performance metrics

### Consumer Features
- **Product Catalog**: Grid with filters
- **Search**: Real-time product search
- **Wishlist**: Save favorites
- **Compare**: Side-by-side comparison
- **Cart**: Rental booking flow

## 🔒 Security Features

- Password hashing
- Session management
- Role-based access (Customer/Admin)
- Audit logging
- Input validation
- CORS protection

## 📝 Database Schema

### Core Tables
- `users` - User authentication
- `customers` - Customer profiles
- `products` - Product inventory
- `categories` - Product categories
- `rentals` - Rental transactions
- `payments` - Payment records
- `returns` - Return processing

### Analytics Tables
- `demand_forecasts` - ML predictions
- `pricing_recommendations` - Price suggestions
- `analytics_reports` - Saved reports
- `customer_activity` - Behavior tracking

## 🧪 Testing

```bash
# Frontend tests
npm test

# Backend tests
pytest backend/tests/
```

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For questions or support, please open an issue on GitHub.

---

Built with ❤️ using React, FastAPI, and Machine Learning