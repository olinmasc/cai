import io
import re
import os
import shutil
import traceback
from lxml import etree
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from database import clients_collection, invoices_collection, filings_collection, reconciliations_collection
from models import ClientCreate, GSTValidationRequest
from dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# ── LIST CLIENTS ──────────────────────────────────────────────

@router.get("/")
async def get_clients(current_user=Depends(get_current_user)):
    ca_id = current_user.get("ca_id", str(current_user["_id"]))
    clients = await clients_collection.find({"ca_id": ca_id}).to_list(100)
    return [serialize(c) for c in clients]


# ── ADD CLIENT ────────────────────────────────────────────────

@router.post("/")
async def add_client(client: ClientCreate, current_user=Depends(get_current_user)):
    ca_id = current_user.get("ca_id", str(current_user["_id"]))

    existing = await clients_collection.find_one(
        {"ca_id": ca_id, "gstin": client.gstin}
    )
    if existing:
        raise HTTPException(400, "Client already exists")

    new_client = {
        "ca_id": ca_id,
        "name": client.name,
        "gstin": client.gstin,
        "phone": client.phone,
        "plan_type": client.plan_type,
        "status": "active",
        "risk_score": 0,
        "last_uploaded_file": None,
        "created_at": datetime.utcnow().isoformat()
    }

    result = await clients_collection.insert_one(new_client)
    new_client["id"] = str(result.inserted_id)
    del new_client["_id"]
    return new_client


# ── DELETE CLIENT ─────────────────────────────────────────────

@router.delete("/{client_id}")
async def delete_client(client_id: str, current_user=Depends(get_current_user)):
    if current_user.get("role") != "Admin":
        raise HTTPException(403, "Only admin")

    await clients_collection.delete_one({"_id": ObjectId(client_id)})
    await invoices_collection.delete_many({"client_id": client_id})
    await filings_collection.delete_many({"client_id": client_id})
    await reconciliations_collection.delete_many({"client_id": client_id})

    return {"message": "deleted"}


# ── VALIDATE GST ──────────────────────────────────────────────

@router.post("/validate-gst")
async def validate_gst(req: GSTValidationRequest, current_user=Depends(get_current_user)):
    valid = len(req.gstin) == 15
    return {
        "gstin": req.gstin,
        "is_valid": valid,
        "legal_name": "Validated Enterprise" if valid else "Unknown",
        "status": "Active" if valid else "Invalid"
    }


# ── UPLOAD TALLY XML (PARSE → invoices_collection) ────────────
# Also saves raw file and sets last_uploaded_file so Run AI works
# regardless of whether upload came from ClientsPage or FilingsPage

@router.post("/{client_id}/upload-xml")
async def upload_tally_xml(
    client_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(404, "Client not found")

    try:
        contents = await file.read()

        # ── Save raw file to /tmp so AI pipeline can find it ──
        upload_dir = "/tmp/cai_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        save_path = f"{upload_dir}/{client_id}.xml"
        with open(save_path, "wb") as f:
            f.write(contents)

        # ── Update client doc with file path ──
        await clients_collection.update_one(
            {"_id": ObjectId(client_id)},
            {"$set": {
                "last_uploaded_file": save_path,
                "last_file_name":     file.filename,
                "last_uploaded_at":   datetime.utcnow().isoformat()
            }}
        )

        # ── Parse XML and insert vouchers into invoices_collection ──
        xml_string = contents.decode("utf-8", errors="ignore")

        start = xml_string.find("<ENVELOPE")
        end = xml_string.rfind("</ENVELOPE>")
        if start != -1 and end != -1:
            xml_string = xml_string[start:end + 11]

        xml_string = re.sub(r'&#[^;]+;', '', xml_string)
        xml_string = xml_string.replace("\x00", "")

        parser = etree.XMLParser(recover=True, huge_tree=True)
        root = etree.fromstring(xml_string.encode(), parser)
        vouchers = root.xpath("//VOUCHER")

        invoices = []
        for v in vouchers:
            date = v.findtext("DATE") or ""
            party = v.findtext("PARTYLEDGERNAME") or "Unknown"
            number = v.findtext("VOUCHERNUMBER") or ""
            gstin = v.findtext("PARTYGSTIN") or ""
            amount = 0

            for l in v.findall(".//ALLLEDGERENTRIES.LIST"):
                amt = l.findtext("AMOUNT")
                if amt:
                    try:
                        amount = abs(float(amt))
                        break
                    except:
                        pass

            invoices.append({
                "client_id":      client_id,
                "invoice_number": number,
                "date":           date,
                "party_name":     party,
                "gstin":          gstin,
                "amount":         amount,
                "gst_type":       "PURCHASE",
                "source":         "tally_xml",
                "status":         "pending",
                "uploaded_at":    datetime.utcnow().isoformat()
            })

        if invoices:
            await invoices_collection.insert_many(invoices)
            return {
                "inserted_count": len(invoices),
                "message": f"Parsed {len(invoices)} vouchers. File saved for AI pipeline."
            }

        raise HTTPException(400, "No vouchers found in XML")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"XML parse error: {str(e)}")


# ── UPLOAD RAW FILE (SAVE → /tmp for AI pipeline) ─────────────
# Used by FilingsPage Upload XML button

@router.post("/{client_id}/upload-file")
async def upload_client_file(
    client_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(404, "Client not found")

    filename = file.filename or ""
    if not (filename.lower().endswith(".xml") or filename.lower().endswith(".csv")):
        raise HTTPException(400, "Only .xml and .csv files are supported.")

    upload_dir = "/tmp/cai_uploads"
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(filename)[1].lower()
    save_path = f"{upload_dir}/{client_id}{ext}"

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    await clients_collection.update_one(
        {"_id": ObjectId(client_id)},
        {"$set": {
            "last_uploaded_file": save_path,
            "last_file_name":     filename,
            "last_uploaded_at":   datetime.utcnow().isoformat()
        }}
    )

    return {
        "message": f"File '{filename}' uploaded for {client['name']}.",
        "path":    save_path
    }
