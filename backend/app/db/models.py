from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime
from app.core.config import settings

# Adjust database URL for SQLAlchemy if needed
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    maturity_level = Column(String, nullable=False) # 'HIGH_MULTI_STORE', 'MEDIUM_EXCEL', 'BASIC_TRADITIONAL'
    description = Column(Text, nullable=True)

class Store(Base):
    __tablename__ = "stores"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    sku = Column(String, index=True, nullable=True)
    barcode = Column(String, index=True, nullable=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    segment = Column(String, default="Standard")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, default="UPI") # UPI, COD, CARD, CASH

class TransactionItem(Base):
    __tablename__ = "transaction_items"
    id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=True)
    category_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    stock_on_hand = Column(Integer, nullable=False)
    reorder_level = Column(Integer, default=10)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    type = Column(String, nullable=False) # 'STOCKOUT_RISK', 'REVENUE_DROP', 'CHURN_WARNING'
    severity = Column(String, default="MEDIUM") # HIGH, MEDIUM, LOW
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    selected_tool = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

