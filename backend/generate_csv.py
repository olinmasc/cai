import pandas as pd
import random
from datetime import datetime, timedelta


def generate_gstin():
    """Generates a realistic Maharashtra (27) GSTIN"""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    # Format: 2 State Code + 10 PAN (5 letters, 4 numbers, 1 letter) + 1 Entity + Z + 1 Checksum
    pan = "".join(random.choices(letters, k=5)) + \
          "".join(random.choices(numbers, k=4)) + \
          random.choice(letters)
    return f"27{pan}1Z{random.choice(numbers)}"


def generate_data(num_records=150):
    parties = [
        "Reliance Industries", "Tata Consultancy", "Sharma Traders",
        "Mehta Supplies", "Rajesh & Co", "Kumar Brothers", "Patel Enterprises",
        "Nandivardhan Pvt Ltd", "HDFC Bank", "Infosys Ltd"
    ]

    data = []
    # Set to March 2026 to match your app's default period
    start_date = datetime(2026, 3, 1)

    for i in range(num_records):
        invoice_date = start_date + timedelta(days=random.randint(0, 30))

        # 5% chance to generate a massive "anomaly" amount to trigger your AI
        if random.random() < 0.05:
            amount = round(random.uniform(500000, 2500000), 2)
        else:
            amount = round(random.uniform(1000, 85000), 2)

        data.append({
            "Invoice No": f"INV-{10000 + i}",
            "Date": invoice_date.strftime("%Y-%m-%d"),
            "Party Name": random.choice(parties),
            "GSTIN": generate_gstin(),
            "Amount": amount,
            "Type": random.choice(["PURCHASE", "SALES"])
        })

    df = pd.DataFrame(data)
    filename = "march_2026_sales.csv"
    df.to_csv(filename, index=False)

    print(f"✅ Success! Generated {num_records} realistic invoices.")
    print(f"📁 File saved as: {filename}")
    print(f"📊 Anomalies injected for AI testing: ~{int(num_records * 0.05)}")


if __name__ == "__main__":
    generate_data(150)
