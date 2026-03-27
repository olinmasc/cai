from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from dependencies import get_current_user
from database import (
    clients_collection,
    reconciliations_collection,
    filings_collection,
)
from reconciliation_engine import run_reconciliation

ai_router = APIRouter(prefix="/ai", tags=["AI Pipeline"])


# ── REQUEST / RESPONSE SCHEMAS ────────────────────────────────

class RunPipelineRequest(BaseModel):
    client_id: str = Field(..., description="The MongoDB _id of the client")
    period: str = "03-2026"


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
    nic_reference: Optional[str] = None
    audit_file: Optional[str] = None
    completed_at: Optional[str] = None
    exceptions: list = []


# ── RUN PIPELINE ──────────────────────────────────────────────

@ai_router.post("/run", response_model=PipelineResponse)
async def run_agent_pipeline(
    req: RunPipelineRequest,
    current_user=Depends(get_current_user),
):
    print(f"DEBUG: Received AI Run Request for Client: {req.client_id}")

    # 1. Validate client ID format
    if not ObjectId.is_valid(req.client_id):
        raise HTTPException(
            400, detail="Invalid Client ID format. Expected a 24-character hex string.")

    # 2. Look up the client
    client = await clients_collection.find_one({"_id": ObjectId(req.client_id)})
    if not client:
        raise HTTPException(404, detail="Client not found.")

    # 3. Get the uploaded file path
    file_path = client.get("last_uploaded_file")
    if not file_path:
        raise HTTPException(
            400,
            detail=(
                f"No source file found for '{client['name']}'. "
                "Please upload a Tally XML or CSV file using the Upload XML button first."
            )
        )

    import os
    if not os.path.exists(file_path):
        raise HTTPException(
            400,
            detail=(
                f"The previously uploaded file for '{client['name']}' could not be found on disk. "
                "Please re-upload the file and try again."
            )
        )

    # 4. Run the reconciliation engine
    try:
        result = await run_reconciliation(req.client_id, file_path)
    except Exception as e:
        print(f"ENGINE ERROR: {e}")
        raise HTTPException(
            500,
            detail="The reconciliation engine failed to process the file. Check the terminal for details."
        )

    risk_score = float(result.get("risk_score", 0))
    total = result.get("total", 0)
    matched = result.get("matched", 0)
    mismatch = result.get("mismatch", 0)

    # 5. Persist results to DB
    now = datetime.utcnow().isoformat()

    await filings_collection.insert_one({
        "client_id":   req.client_id,
        "client_name": client["name"],
        "period":      req.period,
        "status":      "pending",
        "risk_score":  risk_score,
        "created_at":  now,
    })

    await clients_collection.update_one(
        {"_id": ObjectId(req.client_id)},
        {"$set": {"risk_score": risk_score}}
    )

    print(
        f"DEBUG: Pipeline complete — total={total}, matched={matched}, mismatch={mismatch}, risk={risk_score}")

    return {
        "client_id":     req.client_id,
        "client_name":   client["name"],
        "period":        req.period,
        "total_invoices": total,
        "matched":       matched,
        "mismatched":    mismatch,
        "anomalies":     mismatch,
        "risk_score":    risk_score,
        "filing_status": "pending",
        "completed_at":  now,
    }
