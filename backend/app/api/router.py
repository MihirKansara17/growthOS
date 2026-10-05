from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.models import get_db, Tenant, Alert
from app.engine.kpi_engine import KPIEngine
from app.engine.root_cause import RootCauseEngine
from app.engine.rfm_engine import RFMEngine
from app.engine.inventory_engine import InventoryEngine
from app.engine.simulator import SimulatorEngine
from app.ai.ai_orchestrator import AIOrchestrator

router = APIRouter()

class AskRequest(BaseModel):
    tenant_id: str = "tenant_apex"
    prompt: str

class SimulationRequest(BaseModel):
    tenant_id: str = "tenant_apex"
    discount_pct: float = 10.0
    price_change_pct: float = 0.0
    reorder_units: int = 100

@router.get("/tenants")
def get_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).all()

@router.get("/kpis")
def get_kpis(tenant_id: str = "tenant_apex", days: int = 30, db: Session = Depends(get_db)):
    return KPIEngine.calculate_summary(db, tenant_id, days)

@router.get("/categories")
def get_categories(tenant_id: str = "tenant_apex", days: int = 30, db: Session = Depends(get_db)):
    return KPIEngine.category_breakdown(db, tenant_id, days)

@router.get("/root-cause")
def get_root_cause(tenant_id: str = "tenant_apex", days: int = 30, db: Session = Depends(get_db)):
    return RootCauseEngine.analyze_variance(db, tenant_id, days)

@router.get("/rfm")
def get_rfm(tenant_id: str = "tenant_apex", db: Session = Depends(get_db)):
    return RFMEngine.calculate_rfm(db, tenant_id)

@router.get("/inventory")
def get_inventory(tenant_id: str = "tenant_apex", days: int = 30, db: Session = Depends(get_db)):
    return InventoryEngine.get_inventory_health(db, tenant_id, days)

@router.post("/simulate")
def run_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    return SimulatorEngine.simulate_scenario(
        db, req.tenant_id, req.discount_pct, req.price_change_pct, req.reorder_units
    )

@router.get("/alerts")
def get_alerts(tenant_id: str = "tenant_apex", db: Session = Depends(get_db)):
    return db.query(Alert).filter(Alert.tenant_id == tenant_id).all()

@router.post("/ask")
def ask_assistant(req: AskRequest, db: Session = Depends(get_db)):
    return AIOrchestrator.ask_growthos(db, req.tenant_id, req.prompt)
