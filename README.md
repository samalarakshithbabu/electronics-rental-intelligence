# Electronics Rental Intelligence Platform

Smart electronics rental platform with ML-driven demand forecasting, dynamic pricing, and revenue intelligence.

---

## Problem Statement

Electronics are expensive and underutilized; rentals democratize access while ML optimizes pricing and inventory. Rental businesses need demand forecasting, dynamic pricing recommendations, and customer segmentation to maximize revenue.

## Objectives

- Enable secure rental bookings with JWT authentication
- Provide admin analytics dashboard with key metrics
- Forecast demand using ML models
- Recommend dynamic pricing based on demand signals
- Segment customers for targeted marketing

## Key Features

### Implemented
- **User Authentication** - Registration/login with bcrypt + JWT
- **Product Catalog & Rentals** - CRUD operations for electronics inventory and rental bookings
- **Admin Dashboard** - Metrics visualization with Recharts
- **Demand Forecasting** - Heuristic/ML-based demand prediction endpoints
- **Dynamic Pricing** - Pricing recommendations based on demand signals
- **Customer Segmentation** - KMeans clustering (when trained on sufficient data)

### Partially Implemented
- **ML Training Endpoints** - Depend on data volume; require historical booking data
- **PostgreSQL Connectivity** - Configured via environment (SQLite default for development)

### Planned
- Real payment gateway integration (Stripe/Razorpay)
- Docker Compose for production deployment
- Automated model retraining pipeline

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   React     │────▶│   FastAPI   │────▶│  SQLite/         │
│   TypeScript│     │   Backend   │     │  PostgreSQL      │
│   Frontend  │     │             │     │                  │
└─────────────┘     └──────┬──────┘     └──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ scikit-learn│
                    │    Models   │
                    └─────────────┘
```

## Technology Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, Python, SQLAlchemy-style DB layer |
| ML | scikit-learn, joblib |
| Auth | JWT + bcrypt |
| Database | SQLite (dev), PostgreSQL (prod via env) |

## Project Structure

```
electronics-rental-intelligence/
├── src/                    # React TypeScript frontend
├── backend/                # FastAPI backend
│   ├── api/               # API routes
│   ├── db/                # Database models & connection
│   ├── ml/                # ML models (forecasting, pricing, segmentation)
│   ├── security/          # JWT, bcrypt, CORS
│   └── main.py            # Entry point
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── package.json           # Node dependencies
├── Dockerfile.backend     # Backend container
├── docker-compose.yml     # Multi-service (planned)
└── README.md
```

## API Examples

### Authentication
```bash
POST /api/auth/login
Content-Type: application/json

{"username": "user", "password": "pass"}

# Response
{"access_token": "...", "token_type": "bearer"}
```

### Products
```bash
GET /api/products
GET /api/products/{id}
POST /api/products (admin)
PUT /api/products/{id} (admin)
```

### Rentals
```bash
GET /api/rentals
POST /api/rentals
PUT /api/rentals/{id}/return
```

### Analytics & ML
```bash
GET /api/analytics/dashboard
GET /api/ml/forecast/demand
GET /api/ml/pricing/recommendations
GET /api/ml/segmentation/customers
```

## Installation (Windows)

```bash
# 1. Install frontend dependencies
npm install

# 2. Set up backend
cd backend
pip install -r requirements.txt
python init_db.py

# 3. Configure environment
cp .env.example .env
# Edit .env with JWT_SECRET, DATABASE_URL, etc.
```

## Run

```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
cd backend
python main.py
```

- Frontend: http://localhost:5173 (Vite default)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Security

- Password hashing with bcrypt
- JWT tokens with configurable expiry
- CORS configuration
- Role-based access (admin/user)

## Limitations

- SQLite default; PostgreSQL requires environment configuration
- ML metrics from reports not independently verified in this README
- No payment processing implemented
- Docker Compose for production not yet complete
- Model training requires sufficient historical data

---

## Author

**SAMALA RAKSHITH BABU**  

**Contact:**  
- Email: samalarakshithbabu7@gmail.com  
- LinkedIn: https://www.linkedin.com/in/samala-rakshith-babu/  
- GitHub: https://github.com/samalarakshithbabu  

---

## License

MIT License