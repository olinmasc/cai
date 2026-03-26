import os
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from docxtpl import DocxTemplate
from bson import ObjectId
from backend.database import clients_collection

router = APIRouter()

os.makedirs("templates", exist_ok=True)
os.makedirs("generated_reports", exist_ok=True)


@router.get("/generate-blueprint/{client_id}")
async def generate_audit_blueprint(client_id: str):
    try:
        print(f"\n--- Starting generation for: {client_id} ---")
        client = await clients_collection.find_one({"_id": ObjectId(client_id)})

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        context = {
            "company_name": client.get("name", "Unknown Entity"),
            "financial_year_end": "31st March 2026",
            "ca_firm_name": "CAI Associates",
            "firm_registration_no": "123456W",
            "partner_name": "Olin Mascarenhas",
            "membership_no": "987654",
            "sign_place": "Mumbai",
            "sign_date": datetime.now().strftime("%d %B %Y"),
            "tax_disputes": [
                {
                    "statute": "Income Tax Act, 1961",
                    "nature": "Income Tax",
                    "gross": "9,20,700",
                    "deposited": "2,50,000",
                    "period": "A.Y. 2007-08",
                    "forum": "CIT-Appeals"
                }
            ]
        }

        template_path = "templates/statutory_audit_template.docx"
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=500, detail="Template file is missing!")

        print("1. Loading Word Template...")
        doc = DocxTemplate(template_path)

        print("2. Injecting Data...")
        doc.render(context)

        safe_client_name = client.get("name", "client").replace(" ", "_")
        output_filename = f"Draft_{safe_client_name}_{int(datetime.now().timestamp())}.docx"
        output_path = f"generated_reports/{output_filename}"

        print("3. Saving File...")
        doc.save(output_path)

        print("4. Sending to Frontend!")
        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=output_filename
        )

    except Exception as e:
        # IF IT CRASHES, IT PRINTS THE EXACT REASON HERE:
        print("\n❌ ERROR GENERATING DOCUMENT:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
