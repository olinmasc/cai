from fastapi import APIRouter, Depends, HTTPException
from database import filings_collection, clients_collection
from models import FilingCreate
from dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


def serialize(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# ── GET ALL FILINGS FOR A SPECIFIC CLIENT ─────────────────────
@router.get("/{client_id}")
async def get_filings(
    client_id: str,
    current_user=Depends(get_current_user)
):
    filings = await filings_collection.find(
        {"client_id": client_id}
    ).to_list(length=100)
    return [serialize(f) for f in filings]


# ── GET ALL FILINGS ACROSS THE FIRM (dashboard) ───────────────
# FIX: was using str(current_user["_id"]) directly, which broke
# for Clerk users. Clerks share ca_id with their Admin.
@router.get("/")
async def get_all_filings(
    current_user=Depends(get_current_user)
):
    # Both Admin and Clerk have ca_id set correctly at signup
    ca_id = current_user.get("ca_id", str(current_user["_id"]))

    clients = await clients_collection.find(
        {"ca_id": ca_id}
    ).to_list(length=100)

    client_ids = [str(c["_id"]) for c in clients]

    filings = await filings_collection.find(
        {"client_id": {"$in": client_ids}}
    ).to_list(length=500)

    return [serialize(f) for f in filings]


# ── CREATE FILING ──────────────────────────────────────────────
@router.post("/")
async def create_filing(
    filing: FilingCreate,
    current_user=Depends(get_current_user)
):
    client = await clients_collection.find_one(
        {"_id": ObjectId(filing.client_id)}
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    risk_score = client.get("risk_score", 0)

    new_filing = {
        "client_id":   filing.client_id,
        "client_name": client["name"],
        "period":      filing.period,
        "return_type": filing.return_type,
        "status":      "pending",
        "risk_score":  risk_score,
        "filed_at":    None,
        "created_at":  datetime.utcnow().isoformat()
    }

    result = await filings_collection.insert_one(new_filing)
    new_filing["id"] = str(result.inserted_id)
    del new_filing["_id"]
    return new_filing


# ── MARK FILING AS FILED ───────────────────────────────────────
@router.put("/{filing_id}/file")
async def mark_filed(
    filing_id: str,
    current_user=Depends(get_current_user)
):
    result = await filings_collection.update_one(
        {"_id": ObjectId(filing_id)},
        {"$set": {
            "status":   "filed",
            "filed_at": datetime.utcnow().isoformat()
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Filing not found")
    return {"message": "Filing marked as filed"}


# ── MARK FILING AS ERROR ───────────────────────────────────────
@router.put("/{filing_id}/error")
async def mark_error(
    filing_id: str,
    current_user=Depends(get_current_user)
):
    result = await filings_collection.update_one(
        {"_id": ObjectId(filing_id)},
        {"$set": {"status": "error"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Filing not found")
    return {"message": "Filing marked as error"}
