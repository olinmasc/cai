from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from backend.database import invoices_collection, clients_collection
from backend.models import InvoiceCreate
from backend.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime
import xml.etree.ElementTree as ET

router = APIRouter()


def serialize(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# ── GET ALL INVOICES FOR A CLIENT ─────────────────────────────


@router.get("/{client_id}")
async def get_invoices(
    client_id: str,
    current_user=Depends(get_current_user)
):
    invoices = await invoices_collection.find(
        {"client_id": client_id}
    ).to_list(length=500)
    return [serialize(i) for i in invoices]


# ── MANUAL INVOICE ENTRY ───────────────────────────────────────
@router.post("/")
async def add_invoice(
    invoice: InvoiceCreate,
    current_user=Depends(get_current_user)
):
    new_invoice = {
        "client_id": invoice.client_id,
        "date": invoice.date,
        "party_name": invoice.party_name,
        "amount": invoice.amount,
        "gst_type": invoice.gst_type,
        "source": "manual",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    result = await invoices_collection.insert_one(new_invoice)
    new_invoice["id"] = str(result.inserted_id)
    del new_invoice["_id"]
    return new_invoice


# ── TALLY XML UPLOAD ───────────────────────────────────────────
@router.post("/upload/{client_id}")
async def upload_tally_xml(
    client_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    content = await file.read()

    # Parse Tally XML
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Invalid XML file")

    invoices = []
    # Tally stores vouchers — each voucher is one transaction
    for voucher in root.findall(".//VOUCHER"):
        voucher_type = voucher.findtext("VOUCHERTYPENAME", "").strip()

        # Only process sales and purchase vouchers
        if voucher_type.upper() not in ["SALES", "PURCHASE"]:
            continue

        invoice = {
            "client_id": client_id,
            "date": voucher.findtext("DATE", ""),
            "party_name": voucher.findtext("PARTYLEDGERNAME", "Unknown"),
            "amount": abs(float(voucher.findtext("AMOUNT", "0") or "0")),
            "gst_type": voucher_type.upper(),
            "gstin": voucher.findtext("PARTYGSTIN", ""),
            "voucher_number": voucher.findtext("VOUCHERNUMBER", ""),
            "source": "tally",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        invoices.append(invoice)

    if not invoices:
        raise HTTPException(
            status_code=400,
            detail="No sales or purchase vouchers found in this file"
        )

    # Insert all invoices
    result = await invoices_collection.insert_many(invoices)

    return {
        "message": f"{len(invoices)} invoices imported from Tally",
        "count": len(invoices)
    }


# ── DELETE INVOICE ─────────────────────────────────────────────
@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    current_user=Depends(get_current_user)
):
    await invoices_collection.delete_one({"_id": ObjectId(invoice_id)})
    return {"message": "Invoice deleted"}
