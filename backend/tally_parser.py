import xml.etree.ElementTree as ET
import zipfile


def parse_tally_xml(file_path: str):
    invoices = []

    # Check if the uploaded file is a zip archive
    if file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as z:
            # Find the first .xml file inside the zip
            xml_filename = next(
                (name for name in z.namelist() if name.endswith('.xml')), None)
            if not xml_filename:
                raise ValueError("No XML file found inside the zip archive.")

            # Open and parse the XML directly from the zip
            with z.open(xml_filename) as f:
                tree = ET.parse(f)
    else:
        # Parse normally if it's already an uncompressed XML
        tree = ET.parse(file_path)

    root = tree.getroot()

    for voucher in root.iter("VOUCHER"):
        try:
            invoice_no = voucher.findtext("VOUCHERNUMBER")
            date = voucher.findtext("DATE")
            party = voucher.findtext("PARTYLEDGERNAME")

            amount = 0
            for amt in voucher.iter("AMOUNT"):
                try:
                    amount = abs(float(amt.text))
                    break
                except:
                    pass

            invoices.append({
                "invoice_id": invoice_no or "NA",
                "date": date,
                "party_name": party,
                "amount": amount,
                "gst_type": "OTHER"
            })

        except Exception:
            continue

    return invoices
