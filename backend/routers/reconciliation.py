from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from database import reconciliations_collection, clients_collection, audit_logs_collection
from models import NotifyClientRequest
from dependencies import get_current_user, require_admin
from bson import ObjectId
from datetime import datetime
import os
import io
import pandas as pd
from reportlab.pdfgen import canvas
from twilio.rest import Client

router = APIRouter()


def serialize(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# ── FETCH EXCEPTIONS ──────────────────────────────────────────


@router.get("/{client_id}")
async def get_reconciliation(client_id: str, current_user=Depends(get_current_user)):
    """Fetches all logged anomalies and mismatches for a given client."""
    records = await reconciliations_collection.find({"client_id": client_id}).sort("reconciled_at", -1).to_list(length=1000)
    return [serialize(r) for r in records]

# ── APPROVE EXCEPTION (OVERRIDE AI) ───────────────────────────


@router.post("/approve/{exception_id}")
async def approve_exception(exception_id: str, current_admin=Depends(require_admin)):
    """Allows an Admin CA to override an AI-flagged anomaly and clear it from the queue."""
    result = await reconciliations_collection.update_one(
        {"_id": ObjectId(exception_id)},
        {"$set": {
            "status": "approved",
            "approved_by": current_admin["email"],
            "approved_at": datetime.utcnow().isoformat()
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="Exception record not found")

    # Log action for compliance auditing
    await audit_logs_collection.insert_one({
        "action": "OVERRIDE_AI_EXCEPTION",
        "user": current_admin["email"],
        "exception_id": exception_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"message": "Exception overridden and logged to audit trail."}

# ── CLIENT NOTIFICATION (WHATSAPP) ────────────────────────────


@router.post("/notify-client")
async def notify_client(req: NotifyClientRequest, current_admin=Depends(require_admin)):
    """Sends an automated WhatsApp alert to the client regarding a specific invoice anomaly."""
    client = await clients_collection.find_one({"_id": ObjectId(req.client_id)})
    if not client or not client.get("phone"):
        raise HTTPException(
            status_code=400, detail="Client phone number is missing or invalid.")

    phone = client["phone"]

    # Format amount cleanly
    formatted_amount = f"₹{req.amount:,.2f}" if req.amount else "Unknown Amount"

    message_body = (
        f"Hello from {current_admin.get('firm_name', 'your CA Firm')}.\n\n"
        f"Our automated compliance system has detected a mismatch requiring your attention:\n"
        f"Invoice Ref: {req.invoice_no}\n"
        f"Amount: {formatted_amount}\n\n"
        f"Please upload the corrected invoice to our secure portal to avoid filing delays."
    )

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    # Graceful fallback if Twilio is not configured
    if not account_sid or not auth_token:
        print(f"\n[MOCK TWILIO] WhatsApp to {phone}:\n{message_body}\n")
        return {"message": "Twilio not configured. Mock notification logged to console."}

    try:
        tw_client = Client(account_sid, auth_token)
        tw_client.messages.create(
            body=message_body,
            from_=f"whatsapp:{twilio_number}",
            to=f"whatsapp:{phone}"
        )
        return {"message": "WhatsApp notification dispatched successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Twilio Gateway Error: {str(e)}")

# ── EXPORT COMPLIANCE REPORT ──────────────────────────────────


@router.get("/export-report/{client_id}")
async def export_report(client_id: str, format: str = "excel", current_admin=Depends(require_admin)):
    """Generates an Excel or PDF report of all unresolved anomalies for a client."""
    records = await reconciliations_collection.find({
        "client_id": client_id,
        "status": "mismatch"
    }).to_list(length=1000)

    if not records:
        raise HTTPException(
            status_code=404, detail="No active anomalies found for this client.")

    if format == "excel":
        df = pd.DataFrame(records)
        # Clean up columns for the client
        df = df[['party_name', 'invoice_id',
                 'amount', 'mismatch_reason', 'period']]
        df.columns = ['Supplier/Buyer', 'Invoice Number',
                      'Amount (INR)', 'AI Analysis', 'Filing Period']

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Anomalies')
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=GST_Mismatch_Report_{client_id[-6:]}.xlsx"}
        )

    elif format == "pdf":
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "CAI — GST Reconciliation Exception Report")

        p.setFont("Helvetica", 10)
        y = 750
        for rec in records:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(
                50, y, f"Invoice: {rec.get('invoice_id', 'N/A')} | Party: {rec.get('party_name', 'Unknown')}")
            y -= 15
            p.setFont("Helvetica", 10)
            p.drawString(50, y, f"Amount: INR {rec.get('amount', 0.0)}")
            y -= 15
            p.drawString(
                50, y, f"Issue: {rec.get('mismatch_reason', 'Flagged for manual review')}")
            y -= 25

            # Page break handling
            if y < 100:
                p.showPage()
                y = 800

        p.save()
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=GST_Mismatch_Report_{client_id[-6:]}.pdf"}
        )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid format requested. Valid options: 'excel', 'pdf'")


@router.get("/audit/{filename}")
async def download_audit(filename: str):

    path = f"audit_reports/{filename}"

    if not os.path.exists(path):
        raise HTTPException(404, "Audit file not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )
