import io
from lxml import etree
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from database import clients_collection, invoices_collection, filings_collection, reconciliations_collection
from models import ClientCreate, GSTValidationRequest
from dependencies import get_current_user
from bson import ObjectId
from datetime import datetime
import re
import traceback

router = APIRouter()


def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/")
async def get_clients(current_user=Depends(get_current_user)):
    ca_id = current_user.get("ca_id", str(current_user["_id"]))
    clients = await clients_collection.find({"ca_id": ca_id}).to_list(100)
    return [serialize(c) for c in clients]


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
        "created_at": datetime.utcnow().isoformat()
    }

    result = await clients_collection.insert_one(new_client)

    new_client["id"] = str(result.inserted_id)
    del new_client["_id"]

    return new_client


@router.delete("/{client_id}")
async def delete_client(client_id: str, current_user=Depends(get_current_user)):

    if current_user.get("role") != "Admin":
        raise HTTPException(403, "Only admin")

    await clients_collection.delete_one(
        {"_id": ObjectId(client_id)}
    )

    await invoices_collection.delete_many({"client_id": client_id})
    await filings_collection.delete_many({"client_id": client_id})
    await reconciliations_collection.delete_many({"client_id": client_id})

    return {"message": "deleted"}


@router.post("/validate-gst")
async def validate_gst(req: GSTValidationRequest, current_user=Depends(get_current_user)):

    valid = len(req.gstin) == 15

    return {
        "gstin": req.gstin,
        "is_valid": valid,
        "legal_name": "Validated Enterprise" if valid else "Unknown",
        "status": "Active" if valid else "Invalid"
    }


# ✅ FINAL XML PARSER (WORKS WITH TALLY)

@router.post("/{client_id}/upload-xml")
async def upload_tally_xml(
    client_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    client = await clients_collection.find_one(
        {"_id": ObjectId(client_id)}
    )

    if not client:
        raise HTTPException(404, "Client not found")

    try:

        contents = await file.read()

        xml_string = contents.decode(
            "utf-8",
            errors="ignore"
        )

        # -------- CUT TO ENVELOPE --------

        start = xml_string.find("<ENVELOPE")
        end = xml_string.rfind("</ENVELOPE>")

        if start != -1 and end != -1:
            xml_string = xml_string[start:end + 11]

        # remove bad entities like &#4;
        xml_string = re.sub(r'&#[^;]+;', '', xml_string)

        xml_string = xml_string.replace("\x00", "")

        # -------- LXML RECOVER --------

        parser = etree.XMLParser(
            recover=True,
            huge_tree=True
        )

        root = etree.fromstring(
            xml_string.encode(),
            parser
        )

        vouchers = root.xpath("//VOUCHER")

        invoices = []

        for v in vouchers:

            date = v.findtext("DATE") or ""
            party = v.findtext("PARTYLEDGERNAME") or "Unknown"
            number = v.findtext("VOUCHERNUMBER") or ""
            gstin = v.findtext("PARTYGSTIN") or ""

            amount = 0

            ledgers = v.findall(".//ALLLEDGERENTRIES.LIST")

            for l in ledgers:

                amt = l.findtext("AMOUNT")

                if amt:
                    try:
                        amount = abs(float(amt))
                        break
                    except:
                        pass

            invoices.append({

                "client_id": client_id,
                "invoice_number": number,
                "date": date,
                "party_name": party,
                "gstin": gstin,
                "amount": amount,
                "gst_type": "PURCHASE",
                "source": "tally_xml",
                "status": "pending",
                "uploaded_at":
                    datetime.utcnow().isoformat()
            })

        if invoices:

            await invoices_collection.insert_many(invoices)

            return {
                "inserted_count": len(invoices)
            }

        raise HTTPException(400, "No vouchers found")

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            500,
            f"FINAL XML parse error: {str(e)}"
        )
