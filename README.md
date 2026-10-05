# GrowthOS V2 - AI Decision Intelligence Platform for Indian Retail

GrowthOS V2 is a domain-specific, AI-assisted decision-intelligence platform built for Indian retail businesses. It transforms raw retail data into actionable business decisions using a strict diagnostic loop: **Data → Diagnosis → Prediction → Simulation → Recommendation → Action → Measurement**.

---

## 🌟 Key Features

1. **Executive Command Center Dashboard**: Real-time Health Score (0-100), 30-day revenue trends, transaction metrics, and category revenue share distribution.
2. **Automated Root-Cause Variance Engine**: Multi-dimensional variance breakdown (Volume vs. Price/Mix effect, Store drivers, Category drivers).
3. **RFM Customer Intelligence & Churn Alert**: Recency, Frequency, and Monetary segmentation (VIPs, Loyal, At-Risk Churn warnings).
4. **Inventory Days of Cover (DoC) & Stockout Risk**: Velocity forecasting, Days of Cover calculations, and automated purchase order reorder points.
5. **Interactive Scenario Decision Simulator**: Dual-slider what-if simulator projecting 30-day revenue and gross margin impact for promotional discounts & price updates.
6. **"Ask GrowthOS" Grounded AI Assistant**: OpenRouter free models API integration + deterministic grounded rule fallback engine with evidence citations.
7. **Adaptive Multi-Tenant Demo Dataset**: 3 pre-seeded retail profiles (High-Tech Multi-Store, Medium Digital Kirana, Basic Traditional Store) demonstrating graceful degradation.

---

## 🏗️ Architecture & Stack

- **Frontend**: React + TypeScript + Vite (Clean, crisp, light-themed professional enterprise UI; no harsh gradients).
- **Backend**: Python FastAPI + Pydantic v2 + SQLAlchemy ORM (Calculations in Pandas/NumPy).
- **Database**: Supabase PostgreSQL (Free Tier compatible) + SQLite fallback (`growthos.db`).
- **AI Engine**: OpenRouter API (`meta-llama/llama-3.3-70b-instruct:free`) with strict evidence grounding.

---

## 🚀 Quickstart (Local Running)

### 1. Backend Server (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -c "from app.seed.seed_data import seed_database; seed_database()"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- API Documentation: `http://localhost:8000/docs`

### 2. Frontend App (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- Command Center App: `http://localhost:5173` or `http://localhost:5174`

---

## ☁️ 100% Free-Tier Deployment Strategy

- **Frontend**: Deploy on **Vercel** or **Netlify** (Free Static Hosting).
- **Backend**: Deploy on **Render** (Free Web Service).
- **Database**: Deploy on **Supabase** (Free Cloud PostgreSQL).
- **AI Models**: Powered by **OpenRouter Free Tier Models**.
