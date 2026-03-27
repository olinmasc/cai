import re
import os
from lxml import etree
from datetime import datetime
from database import reconciliations_collection
from ml_model import get_detector


def safe_float(val):
    try:
        return abs(float(val))
    except:
        return 0.0


def parse_tally_xml(file_path: str):
    invoices = []
    try:
        with open(file_path, "rb") as f:
            raw = f.read()

        xml_string = raw.decode("utf-8", errors="ignore")

        start = xml_string.find("<ENVELOPE")
        end = xml_string.rfind("</ENVELOPE>")
        if start != -1 and end != -1:
            xml_string = xml_string[start:end + 11]

        xml_string = re.sub(r'&#[^;]+;', '', xml_string)
        xml_string = xml_string.replace("\x00", "")

        parser = etree.XMLParser(recover=True, huge_tree=True)
        root = etree.fromstring(xml_string.encode(), parser)

        vouchers = root.xpath("//VOUCHER")
        print(f"TALLY PARSED: {len(vouchers)} vouchers found")

        for v in vouchers:
            date = v.findtext("DATE") or ""
            party = v.findtext("PARTYLEDGERNAME") or "Unknown"
            number = v.findtext("VOUCHERNUMBER") or "NA"
            amount = 0.0

            for ledger in v.findall(".//ALLLEDGERENTRIES.LIST"):
                amt = ledger.findtext("AMOUNT")
                if amt:
                    val = safe_float(amt)
                    if val > 0:
                        amount = val
                        break

            if amount == 0.0:
                for amt_el in v.iter():
                    if amt_el.tag.upper() == "AMOUNT":
                        val = safe_float(amt_el.text)
                        if val > 0:
                            amount = val
                            break

            invoices.append({
                "invoice_id": number,
                "date":       date,
                "party_name": party,
                "amount":     amount,
                "gst_type":   "OTHER"
            })

    except Exception as e:
        print(f"XML PARSE ERROR: {e}")

    print(f"TALLY PARSED: {len(invoices)} invoices extracted")
    return invoices


def load_invoices(file_path: str):
    if not os.path.exists(file_path):
        print(f"FILE NOT FOUND: {file_path}")
        return []

    try:
        with open(file_path, "r", errors="ignore") as f:
            text = f.read(5000)
    except Exception as e:
        print(f"FILE READ ERROR: {e}")
        return []

    # 1. Check the file extension directly (Fast & Reliable)
    lower_path = file_path.lower()
    if lower_path.endswith('.xml') or lower_path.endswith('.zip'):
        print("Detected XML/ZIP file by extension - routing to parser")
        return parse_tally_xml(file_path)

    # 2. Fallback: Check the content for other types of files
    text_upper = text.upper()
    if "ENVELOPE" in text_upper or "TALLYREQUEST" in text_upper or "VOUCHER" in text_upper:
        print("Detected Tally XML by content - routing to parser")
        return parse_tally_xml(file_path)

    print(f"Unsupported file format: {file_path}")
    return []


async def run_reconciliation(client_id: str, file_path: str):
    try:
        print(f"RECON: Starting for client {client_id}, file {file_path}")

        invoices = load_invoices(file_path)

        if not invoices:
            raise Exception("No invoices parsed — check the XML structure")

        print(
            f"RECON: {len(invoices)} invoices loaded, running anomaly detection...")

        detector = get_detector()
        scored = detector.predict_anomaly(invoices)

        total = len(scored)
        matched = 0
        mismatch = 0
        risk_sum = 0
        results = []

        for inv in scored:
            score = float(inv.get("anomaly_score", 0))
            risk_sum += score

            if score < 50:
                matched += 1
            else:
                mismatch += 1
                results.append({
                    "client_id":       client_id,
                    "invoice_id":      inv["invoice_id"],
                    "party_name":      inv["party_name"],
                    "amount":          inv["amount"],
                    "mismatch_reason": "AI anomaly detected",
                    "status":          "mismatch",
                    "period":          datetime.utcnow().strftime("%Y-%m"),
                    "reconciled_at":   datetime.utcnow().isoformat()
                })

        if results:
            await reconciliations_collection.insert_many(results)

        risk_score = round(risk_sum / total, 1) if total > 0 else 0

        print(
            f"RECON: Complete — total={total}, matched={matched}, mismatch={mismatch}, risk={risk_score}")

        return {
            "total":      total,
            "matched":    matched,
            "mismatch":   mismatch,
            "risk_score": risk_score
        }

    except Exception as e:
        print(f"RECON ERROR: {e}")
        raise Exception(f"Pipeline failed: {str(e)}")
