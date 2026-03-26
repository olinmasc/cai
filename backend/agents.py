"""
agents.py — CAI Multi-Agent Orchestration via LangGraph
"""

import os
from datetime import datetime
from typing import TypedDict, Optional
from dotenv import load_dotenv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from ml_model import get_detector
from mlops import get_tracker, retrain_and_log

load_dotenv()

# =========================
# LLM SETUP
# =========================
groq_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=groq_key,
    temperature=0.1,
) if groq_key else None


# =========================
# STATE
# =========================
class PipelineState(TypedDict):
    client_id: str
    client_name: str
    period: str
    ca_email: str
    invoices: list
    ingested_invoices: list
    reconciled_invoices: list
    matched_count: int
    mismatch_count: int
    anomalies: list
    risk_score: float
    filing_status: str
    nic_reference: Optional[str]
    completed_at: Optional[str]
    model_metrics: dict


# =========================
# INGESTION AGENT
# =========================
async def ingestion_agent(state: PipelineState) -> PipelineState:
    invoices = state.get("invoices", [])
    ingested = []

    for inv in invoices:
        try:
            ingested.append({
                "id": inv.get("id", f"inv_{datetime.utcnow().timestamp()}"),
                "party_name": inv.get("party_name", ""),
                "amount": float(inv.get("amount", 0)),
                "gstin": inv.get("gstin", "").strip().upper(),
                "gst_type": inv.get("gst_type", "PURCHASE").upper(),
            })
        except Exception:
            pass

    return {
        **state,
        "ingested_invoices": ingested,
    }


# =========================
# RECONCILIATION AGENT (The ML Brain)
# =========================
async def reconciliation_agent(state: PipelineState) -> PipelineState:
    detector = get_detector()
    invoices = state.get("ingested_invoices", [])

    if not invoices:
        return {**state, "risk_score": 0.0, "matched_count": 0, "mismatch_count": 0, "anomalies": []}

    scored = detector.predict_anomaly(invoices)

    reconciled = []
    matched = 0
    mismatched = 0
    anomalies = []

    for inv in scored:
        anomaly_score = inv.get("anomaly_score", 0)
        is_anomaly = inv.get("is_anomaly", False)
        missing_data = not inv.get("gstin") or inv.get("amount") <= 0
        gstr2a_match = not (is_anomaly or missing_data)
        mismatch_reason = None

        if not gstr2a_match:
            mismatched += 1
            if missing_data:
                raw_reason = "Critical data missing (GSTIN or Amount is zero/null)."
            else:
                raw_reason = f"XGBoost model flagged transactional pattern anomaly (Confidence: {anomaly_score}%)."

            if llm:
                try:
                    response = llm.invoke(
                        f"You are a strict GST compliance AI for Indian Chartered Accountants. "
                        f"A mismatch was detected: '{raw_reason}'. "
                        f"Invoice amount: ₹{inv['amount']}. Party: {inv['party_name']}. "
                        f"Provide a 1-sentence, highly professional instruction on what the CA must verify before filing. Do not use quotes."
                    )
                    mismatch_reason = response.content.strip()
                except Exception:
                    mismatch_reason = raw_reason
            else:
                mismatch_reason = raw_reason
        else:
            matched += 1

        result = {
            **inv,
            "gstr2a_match": gstr2a_match,
            "mismatch_reason": mismatch_reason,
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly,
            "status": "matched" if gstr2a_match else "mismatch",
        }
        reconciled.append(result)

        if is_anomaly or not gstr2a_match:
            anomalies.append(result)

    mismatch_rate = mismatched / len(reconciled)
    anomaly_rate = len(
        [a for a in anomalies if a.get("is_anomaly")]) / len(reconciled)
    risk_score = round((mismatch_rate * 60 + anomaly_rate * 40), 1)

    return {
        **state,
        "reconciled_invoices": reconciled,
        "matched_count": matched,
        "mismatch_count": mismatched,
        "anomalies": anomalies,
        "risk_score": risk_score,
    }


# =========================
# FILING AGENT
# =========================
async def filing_agent(state: PipelineState) -> PipelineState:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    nic = f"NIC{timestamp}"

    return {
        **state,
        "filing_status": "filed",
        "nic_reference": nic,
    }


# =========================
# LEARNING AGENT
# =========================
async def learning_agent(state: PipelineState) -> PipelineState:
    detector = get_detector()

    confirmed_anomaly_ids = [
        inv["id"] for inv in state.get("anomalies", [])
        if not inv.get("gstr2a_match") and inv.get("is_anomaly")
    ]

    metrics = {}
    if state.get("reconciled_invoices"):
        metrics = retrain_and_log(
            detector=detector,
            new_invoices=state["reconciled_invoices"],
            confirmed_anomalies=confirmed_anomaly_ids,
        )

    return {
        **state,
        "model_metrics": metrics,
        "completed_at": datetime.utcnow().isoformat()
    }


# =========================
# CONDITIONAL ROUTER
# =========================
def should_file(state: PipelineState) -> str:
    if state["risk_score"] > 60.0 or len(state.get("ingested_invoices", [])) == 0:
        return "skip_filing"
    return "file"


# =========================
# GRAPH
# =========================
def build_pipeline():
    graph = StateGraph(PipelineState)

    graph.add_node("ingestion", ingestion_agent)
    graph.add_node("reconciliation", reconciliation_agent)
    graph.add_node("filing", filing_agent)
    graph.add_node("learning", learning_agent)

    graph.set_entry_point("ingestion")
    graph.add_edge("ingestion", "reconciliation")
    graph.add_conditional_edges(
        "reconciliation",
        should_file,
        {
            "file": "filing",
            "skip_filing": "learning",
        }
    )
    graph.add_edge("filing", "learning")
    graph.add_edge("learning", END)

    return graph.compile()


pipeline = build_pipeline()


# =========================
# RUN PIPELINE
# =========================
async def run_pipeline(
    client_id: str,
    client_name: str,
    period: str,
    ca_email: str,
    invoices: list = None,
) -> dict:

    state: PipelineState = {
        "client_id": client_id,
        "client_name": client_name,
        "period": period,
        "ca_email": ca_email,
        "invoices": invoices or [],
        "ingested_invoices": [],
        "reconciled_invoices": [],
        "matched_count": 0,
        "mismatch_count": 0,
        "anomalies": [],
        "risk_score": 0,
        "filing_status": "pending",
        "nic_reference": None,
        "completed_at": None,
        "model_metrics": {},
    }

    final_state = await pipeline.ainvoke(state)

    total = len(final_state.get("ingested_invoices", []))
    matched = final_state.get("matched_count", 0)
    mismatched = final_state.get("mismatch_count", 0)
    anomalies = final_state.get("anomalies", [])
    risk = final_state.get("risk_score", 0)
    nic = final_state.get("nic_reference", "")
    completed = final_state.get("completed_at", "")

    # ── FIX: Write to /tmp on Vercel (filesystem is read-only) ──
    tmp_dir = "/tmp/audit_reports"
    os.makedirs(tmp_dir, exist_ok=True)
    filename = f"GST_AUDIT_{client_id}_{period}.pdf"
    path = os.path.join(tmp_dir, filename)

    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "CAI — GST Compliance Audit Report")

    c.setFont("Helvetica", 12)
    y = 720
    c.drawString(50, y, f"Client: {client_name}")
    y -= 20
    c.drawString(50, y, f"Period: {period}")
    y -= 20
    c.drawString(50, y, f"Total: {total}")
    y -= 20
    c.drawString(50, y, f"Matched: {matched}")
    y -= 20
    c.drawString(50, y, f"Mismatched: {mismatched}")
    y -= 20
    c.drawString(50, y, f"Risk: {risk}%")
    y -= 20
    c.drawString(50, y, f"NIC: {nic}")
    y -= 30

    for ex in anomalies:
        party = ex.get('party_name', 'Unknown')
        amt = ex.get('amount', 0)
        reason = ex.get('mismatch_reason', 'Flagged for review')

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, f"{party} | ₹{amt}")
        y -= 15

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Reason: {reason[:100]}...")
        y -= 25

        if y < 100:
            c.showPage()
            y = 750

    c.save()

    return {
        "client_id": client_id,
        "client_name": client_name,
        "period": period,
        "total_invoices": total,
        "matched": matched,
        "mismatched": mismatched,
        "anomalies": len(anomalies),
        "risk_score": risk,
        "filing_status": final_state.get("filing_status"),
        "nic_reference": nic,
        "audit_file": filename,
        "completed_at": completed,
        "exceptions": anomalies,
    }
