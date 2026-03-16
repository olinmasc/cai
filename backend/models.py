from pydantic import BaseModel
from typing import Optional

# ── AUTH ──────────────────────────────────────────


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Admin"  # Admin or Clerk
    firm_name: Optional[str] = None  # Required if Admin
    admin_email: Optional[str] = None  # Required if Clerk to link accounts


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

# ── CLIENTS ───────────────────────────────────────


class ClientCreate(BaseModel):
    name: str
    gstin: str
    phone: str
    plan_type: str = "pilot"


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    plan_type: Optional[str] = None


class GSTValidationRequest(BaseModel):
    gstin: str

# ── RECONCILIATION & NOTIFICATION ─────────────────


class NotifyClientRequest(BaseModel):
    client_id: str
    invoice_no: str
    amount: float

# ── INVOICES ───────────────────────────


class InvoiceCreate(BaseModel):
    client_id: str
    date: str
    party_name: str
    amount: float
    gst_type: str

# ── FILINGS ────────────────────────────


class FilingCreate(BaseModel):
    client_id: str
    period: str
    return_type: str = "GSTR-3B"
