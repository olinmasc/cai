"""
ai_routes.py — FastAPI routes that trigger the AI pipeline
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from dependencies import get_current_user
from database import (
    clients_collection,
    invoices_collection,
    reconciliations_collection,
    filings_collection,
)

from agents import run_pipeline
from ml_model import get_detector
from bson import ObjectId


ai_router = APIRouter(prefix="/ai", tags=["AI Pipeline"])


# =========================
# MODELS
# =========================

class RunPipelineRequest(BaseModel):
    client_id: str
    period: str = "03-2026"
    use_stored_invoices: bool = True


class PipelineResponse(BaseModel):

    client_id: str
    client_name: str
    period: str

    total_invoices: int
    matched: int
    mismatched: int
    anomalies: int

    risk_score: float

    filing_status: str
    nic_reference: Optional[str]

    audit_file: Optional[str]

    completed_at: Optional[str]

    exceptions: list = []


# =========================
# RUN PIPELINE
# =========================

@ai_router.post("/run", response_model=PipelineResponse)
async def run_agent_pipeline(
    req: RunPipelineRequest,
    current_user=Depends(get_current_user),
):

    # ---------- GET CLIENT ----------

    client = await clients_collection.find_one(
        {"_id": ObjectId(req.client_id)}
    )

    if not client:
        raise HTTPException(404, "Client not found")

    # ---------- GET INVOICES ----------

    invoices = []

    if req.use_stored_invoices:

        raw = await invoices_collection.find(
            {"client_id": req.client_id}
        ).to_list(500)

        invoices = [
            {
                "party_name": inv.get("party_name", ""),
                "amount": float(inv.get("amount", 0)),
                "gstin": inv.get("gstin", ""),
            }
            for inv in raw
        ]

    # ---------- RUN PIPELINE ----------

    try:

        result = await run_pipeline(
            client_id=str(client["_id"]),
            client_name=client["name"],
            period=req.period,
            ca_email=current_user["email"],
            invoices=invoices,
        )

    except Exception as e:

        print("PIPELINE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    risk_score = float(result.get("risk_score", 0))

    # ---------- SAVE RECON ----------

    if result.get("anomalies"):

        await reconciliations_collection.insert_one({
            "client_id": req.client_id,
            "period": req.period,
            "risk_score": risk_score,
            "created_at": datetime.utcnow().isoformat(),
        })

    # ---------- SAVE FILING ----------

    await filings_collection.insert_one({

        "client_id": req.client_id,
        "client_name": client["name"],
        "period": req.period,
        "status": result.get("filing_status"),
        "nic_reference": result.get("nic_reference"),
        "risk_score": risk_score,
        "created_at": datetime.utcnow().isoformat(),

    })

    # ---------- UPDATE CLIENT ----------

    await clients_collection.update_one(

        {"_id": ObjectId(req.client_id)},

        {"$set": {"risk_score": risk_score}}

    )

    # ---------- RETURN ----------

    return {

        "client_id": req.client_id,
        "client_name": client["name"],
        "period": req.period,

        "total_invoices": result.get("total_invoices", 0),
        "matched": result.get("matched", 0),
        "mismatched": result.get("mismatched", 0),
        "anomalies": result.get("anomalies", 0),

        "risk_score": risk_score,

        "filing_status": result.get("filing_status"),
        "nic_reference": result.get("nic_reference"),

        "audit_file": result.get("audit_file"),  # ✅ IMPORTANT

        "completed_at": result.get("completed_at"),

        "exceptions": [],

    }


# =========================
# STATUS
# =========================

@ai_router.get("/status")
async def get_ai_status(current_user=Depends(get_current_user)):

    detector = get_detector()

    return {

        "model_trained": detector.is_trained,

        "agents": [
            {"name": "Ingestion", "status": "ready"},
            {"name": "Reconciliation", "status": "ready"},
            {"name": "Filing", "status": "ready"},
            {"name": "Learning", "status": "ready"},
        ],

    }
