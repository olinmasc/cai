from routers import auth, clients, invoices, reconciliation, filings
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from ai_routes import ai_router
import pandas as pd
import io
import math
import re
from datetime import datetime
from bson import ObjectId
from database import invoices_collection, clients_collection
import audit

app = FastAPI(title="CAI — Autonomous GST Compliance", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_router = APIRouter(prefix="/clients", tags=["Client Data Upload"])


@upload_router.post("/{client_id}/upload-invoices")
async def upload_real_invoices(client_id: str, file: UploadFile = File(...)):
    """Smart ingestion: Auto-cleans dirty data, fixes formatting, and validates."""
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=400, detail="Only .csv, .xls, or .xlsx files are allowed.")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Could not read file. It might be corrupted.")

    # ── 1. SAFE AUTO-CLEANING LAYER ──

    # Drop rows that are completely empty
    df.dropna(how='all', inplace=True)

    # Standardize column names
    df.columns = [str(c).strip().title() for c in df.columns]

    # Map common CA aliases to our standard format
    col_mapping = {
        'Invoice Number': 'Invoice No',
        'Inv No': 'Invoice No',
        'Gst Number': 'Gstin',
        'Gst': 'Gstin',
        'Party': 'Party Name'
    }
    df.rename(columns=col_mapping, inplace=True)

    required_columns = ['Invoice No', 'Amount']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=400, detail=f"Missing mandatory columns: {', '.join(missing_cols)}")

    # ── THE FIX: SMART CURRENCY SCRUBBING ──
    df['Amount'] = df['Amount'].astype(str)
    df['Amount'] = df['Amount'].str.replace(
        ',', '', regex=False)               # Removes commas
    # Removes Rs or Rs. (case insensitive)
    df['Amount'] = df['Amount'].str.replace(r'(?i)rs\.?', '', regex=True)
    df['Amount'] = df['Amount'].str.replace(
        '₹', '', regex=False)               # Removes Rupee symbol
    df['Amount'] = df['Amount'].str.replace(
        ' ', '', regex=False)               # Removes spaces

    # Convert safely to numeric!
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    df['Invoice No'] = df['Invoice No'].astype(str).str.strip()

    # ── 2. VALIDATION & DATABASE INSERTION ──

    row_errors = []
    valid_invoices = []

    for index, row in df.iterrows():
        row_num = index + 2

        invoice_no = str(row.get('Invoice No', '')).strip()
        if not invoice_no or invoice_no.lower() == 'nan':
            row_errors.append(f"Row {row_num}: Invoice Number is missing.")
            continue

        amount = row.get('Amount', 0)
        if math.isnan(amount):
            row_errors.append(
                f"Row {row_num}: Amount is not a valid number. We cannot guess this.")
            continue

        valid_invoices.append({
            "client_id": client_id,
            "invoice_number": invoice_no,
            "date": str(row.get('Date', datetime.utcnow().strftime("%Y-%m-%d"))),
            "party_name": str(row.get('Party Name', 'Unknown')),
            "gstin": str(row.get('Gstin', '')).strip(),
            "amount": float(amount),
            "gst_type": str(row.get('Type', 'PURCHASE')).upper(),
            "source": "excel_upload",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat()
        })

    if row_errors:
        error_msg = "File Rejected. We auto-cleaned what we could, but please fix these critical errors:\n• " + \
            "\n• ".join(row_errors[:5])
        if len(row_errors) > 5:
            error_msg += f"\n...and {len(row_errors) - 5} more."
        raise HTTPException(status_code=400, detail=error_msg)

    if valid_invoices:
        await invoices_collection.insert_many(valid_invoices)

    return {
        "message": "Upload successful",
        "inserted_count": len(valid_invoices),
        "filename": file.filename
    }

app.include_router(upload_router)

app.include_router(auth.router,           prefix="/auth",
                   tags=["Auth"])
app.include_router(clients.router,        prefix="/clients",
                   tags=["Clients"])
app.include_router(invoices.router,
                   prefix="/invoices",       tags=["Invoices"])
app.include_router(reconciliation.router,
                   prefix="/reconciliation", tags=["Reconciliation"])
app.include_router(filings.router,        prefix="/filings",
                   tags=["Filings"])
app.include_router(ai_router)
app.include_router(audit.router,          prefix="/audit",
                   tags=["Audit Reports"])


@app.get("/")
async def root():
    return {"message": "CAI API is running", "version": "1.0.0"}
